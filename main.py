from functions.classes.APIService import APIService
from functions.classes.Account import get_account
from functions.classes.Secret import get_secret
from functions.sellAllItems import sellAllItems
from functions.utils import getCrystalBalance, getJewelBalance, sendCrystal, sendJewel, buyCrystal, getCrystalPriceJewel, heroNumber, createETHAddress, fillGas
from functions.save_encryption import saveEncryption
from functions.send_heros import sendHeros
from functions.classes.RPCProvider import get_rpc_provider
from functions.classes.TablesManager import TablesManager
from functions.classes.Config import secretName, isProd
import time

def main(logger):
    tablesManager = TablesManager(isProd)
    rpcProvider = get_rpc_provider("dfk", [], logger)
    apiService = APIService(rpcProvider.chain)
    secret = get_secret(secretName)
    warehouse_address = tablesManager.accounts.scan(
            FilterExpression="warehouse = :warehouse",
            ExpressionAttributeValues={
                ":warehouse": True
            })["Items"][0]["address_"]
    trader_address = tablesManager.accounts.scan(
            FilterExpression="trader = :trader",
            ExpressionAttributeValues={
                ":trader": True
            })["Items"][0]["address_"]
    setup_address = tablesManager.accounts.scan(
            FilterExpression="setup = :setup",
            ExpressionAttributeValues={
                ":setup": True
            })["Items"][0]["address_"]
    
    buyer_settings = tablesManager.autoplayer.get_item(Key={"key_": "buyer_settings"})["Item"]
    profit_address = buyer_settings["profit_address"]



    enabled_refiller = buyer_settings["refiller"]
    enabled_profit = buyer_settings["profit"]
    refiller_min_buffer = float(buyer_settings["refiller_min_buffer"])
    refiller_max_buffer = float(buyer_settings["refiller_max_buffer"])
    buyer_min_buffer = float(buyer_settings["buyer_min_buffer"])
    buyer_refill_amount = float(buyer_settings["buyer_refill_amount"])
    profit_amount = float(buyer_settings["profit_amount"])

    setup_account = get_account(tablesManager, secret, setup_address, rpcProvider)

    warehouse_account = get_account(tablesManager, secret, warehouse_address, rpcProvider)

    trader_account = get_account(tablesManager, secret, trader_address, rpcProvider)

    if enabled_refiller:
        if refiller_min_buffer*10**18 < getJewelBalance(setup_account, rpcProvider) and getCrystalBalance(warehouse_account, apiService , rpcProvider) < buyer_min_buffer*10**18:

            crystal_value = getCrystalPriceJewel(apiService , rpcProvider) 
            crystal_amount = int(buyer_refill_amount*10**18)
            expected_cost = int(crystal_amount*crystal_value*1.05)
            print("Refilling buyer account")
            print(f"Buying {buyer_refill_amount} crystals")
            logger.info(f"Refilling buyer account with {buyer_refill_amount} crystals")

            setup_account.update_nonce(rpcProvider)
            buyCrystal(setup_account, crystal_amount, expected_cost, apiService , rpcProvider)

            print(f"Sending {buyer_refill_amount} crystals to buyer")
            logger.info(f"Sending {buyer_refill_amount} crystals to buyer")

            setup_account.update_nonce(rpcProvider)
            sendCrystal(warehouse_account, setup_account, crystal_amount, apiService , rpcProvider)

    if enabled_profit:
            if  refiller_max_buffer*10**18 < getJewelBalance(setup_account, rpcProvider):
                jewel_amount = int(profit_amount*10**18)
                setup_account.update_nonce(rpcProvider)
                sendJewel(profit_address, setup_account, jewel_amount, rpcProvider)
                tablesManager.profit_tracking.put_item(
                        Item={
                            "time_": str(time.time()),
                            "amount": str(profit_amount),
                            "from": setup_address,
                            "address": profit_address
                        }
                )
            if refiller_max_buffer*10**18 < getJewelBalance(trader_account, rpcProvider):
                jewel_amount = int(profit_amount*10**18)
                trader_account.update_nonce(rpcProvider)
                sendJewel(profit_address, trader_account, jewel_amount, rpcProvider)
                tablesManager.profit_tracking.put_item(
                        Item={
                            "time_": str(time.time()),
                            "amount": str(profit_amount),
                            "from": trader_address,
                            "address": profit_address
                        }
                )

    active_orders = tablesManager.active_orders.scan()
    has_active_orders  = len(active_orders["Items"]) > 0 if "Items" in active_orders else False

    if not has_active_orders:
        print("Checking items to sell")
        logger.info("Checking items to sell")
        sellAllItems(trader_account, apiService, rpcProvider)

    
    warehouse_heros = heroNumber(warehouse_account, apiService , rpcProvider)

    deployer_settings = tablesManager.autoplayer.get_item(Key={"key_": "deployer_settings"})["Item"]

    enabled_deployer = deployer_settings["enabled"]
    if isProd:
        last_account_address = deployer_settings["last_account"]
    else:
        last_account_address = deployer_settings["last_account_dev"]
    gas_fill_amount = int(deployer_settings["gas_fill_amount"])

    managers = tablesManager.managers.scan(
        FilterExpression="is_default = :is_default",
            ExpressionAttributeValues={
                ":is_default": False
            }
    )["Items"]
    default_manager_address = tablesManager.managers.scan(
            FilterExpression="is_default = :is_default",
            ExpressionAttributeValues={
                ":is_default": True
            })["Items"][0]["address_"]
    
    for manager in managers:
        if manager['prod'] != isProd: continue
        target_accounts = tablesManager.managers.get_item(Key={"address_": manager['address_']})["Item"]["target_accounts"]
        current_accounts = len(tablesManager.accounts.scan(
                FilterExpression="pay_to = :manager_",
                ExpressionAttributeValues={
                    ":manager_": manager['address_'],
                })["Items"])
        if current_accounts < int(target_accounts):
            manager_address = manager['address_']
            break
        else:
            manager_address = default_manager_address

    
    if not enabled_deployer: return "Deployer is disabled"
    last_account = get_account(tablesManager, secret, last_account_address, rpcProvider)
    last_acc_jewel_balance = getJewelBalance(last_account, rpcProvider)
    last_acc_hero_number = heroNumber(last_account, apiService , rpcProvider)
    if 6 > warehouse_heros: return "Warehouse does not have enough heros"
    if 18 <= last_acc_hero_number and last_acc_jewel_balance != 0:
        print("Last account has 18 heros and jewel balance")
        print("creating new account")
        new_account = createETHAddress()
        saveEncryption(tablesManager, secret, new_account["address"], new_account["private_key"], manager_address)
        deployed_account = get_account(tablesManager, secret, new_account["address"], rpcProvider)
        print(f"New account created: {new_account['address']}")
        if isProd:
            tablesManager.autoplayer.update_item(
                    Key={"key_": "deployer_settings"},
                    UpdateExpression="SET last_account = :account",
                    ExpressionAttributeValues={":account": new_account["address"]}
            )
        else:
            tablesManager.autoplayer.update_item(
                    Key={"key_": "deployer_settings"},
                    UpdateExpression="SET last_account_dev = :account",
                    ExpressionAttributeValues={":account": new_account["address"]}
            )
    else:
        deployed_account = last_account
    
    hero_number = heroNumber(deployed_account, apiService , rpcProvider)
    jewel_balance = getJewelBalance(deployed_account, rpcProvider)

    print(f"Account has {hero_number} heros")
    logger.info(f"Account has {hero_number} heros")

    print(f"Account has {jewel_balance} jewel")
    logger.info(f"Account has {jewel_balance} jewel")

    if 18 <= hero_number and jewel_balance != 0:
        return "Account is already deployed"
    if jewel_balance == 0:
        print("Adding Gas")
        logger.info("Adding Gas")
        setup_account.update_nonce(rpcProvider)
        fillGas(deployed_account, setup_account, gas_fill_amount*10**18, rpcProvider)
        print(f"Filled gas to account {deployed_account.address}")
        logger.info(f"Filled gas to account {deployed_account.address}")
    if 18 <= hero_number:
        print("Account already has 18 heros")
        logger.info("Account already has 18 heros")
    else:
        amount = min(18-hero_number, warehouse_heros)
        print("Getting heros from warehouse")
        logger.info("Getting heros from warehouse")
        sendHeros(deployed_account, warehouse_account, amount, apiService, rpcProvider)

    return "Done"