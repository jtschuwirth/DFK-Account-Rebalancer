from functions.getAccount import get_account
from functions.getSecret import get_secret
from functions.sellAllItems import sellAllItems
from functions.utils import getCrystalBalance, getJewelBalance, sendCrystal, sendJewel, buyCrystal, getCrystalPriceJewel, heroNumber, createETHAddress, fillGas
from functions.save_encryption import saveEncryption
from functions.send_heros import sendHeros
from functions.classes.RPCProvider import get_rpc_provider
from functions.classes.TablesManager import TablesManager
import time
import os
from dotenv import load_dotenv

load_dotenv()

tablesManager = TablesManager(os.environ["PROD"] == "true")
disabled_rpc_list = tablesManager.autoplayer.get_item(Key={"key_": "autoplayer_settings"})["Item"]["disabled_rpc_list"]
secret = get_secret(os.environ["PROD"] == "true")

def main(event, context, logger):
    RPCProvider = get_rpc_provider("dfk", disabled_rpc_list, logger)
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
    
    buyer_settings = tablesManager.autoplayer.get_item(Key={"key_": "buyer_settings"})["Item"]
    setup_address = buyer_settings["refiller_address"]
    profit_address = buyer_settings["profit_address"]



    enabled_refiller = buyer_settings["refiller"]
    enabled_profit = buyer_settings["profit"]
    refiller_min_buffer = float(buyer_settings["refiller_min_buffer"])
    refiller_max_buffer = float(buyer_settings["refiller_max_buffer"])
    buyer_min_buffer = float(buyer_settings["buyer_min_buffer"])
    buyer_refill_amount = float(buyer_settings["buyer_refill_amount"])
    profit_amount = float(buyer_settings["profit_amount"])

    setup_account = get_account(tablesManager, secret, setup_address, RPCProvider.w3)
    setup_nonce = RPCProvider.w3.eth.get_transaction_count(setup_account.address)

    warehouse_account = get_account(tablesManager, secret, warehouse_address, RPCProvider.w3)
    warehouse_nonce = RPCProvider.w3.eth.get_transaction_count(warehouse_account.address)

    trader_account = get_account(tablesManager, secret, trader_address, RPCProvider.w3)
    trader_nonce = RPCProvider.w3.eth.get_transaction_count(trader_account.address)

    if enabled_refiller:
        if refiller_min_buffer*10**18 < getJewelBalance(setup_account, RPCProvider) and getCrystalBalance(warehouse_account, RPCProvider) < buyer_min_buffer*10**18:

            crystal_value = getCrystalPriceJewel(RPCProvider) 
            crystal_amount = int(buyer_refill_amount*10**18)
            expected_cost = int(crystal_amount*crystal_value*1.05)
            print("Refilling buyer account")
            print(f"Buying {buyer_refill_amount} crystals")
            logger.info(f"Refilling buyer account with {buyer_refill_amount} crystals")
            buyCrystal(setup_account, crystal_amount, expected_cost, setup_nonce, RPCProvider)
            setup_nonce+=1
            print(f"Sending {buyer_refill_amount} crystals to buyer")
            logger.info(f"Sending {buyer_refill_amount} crystals to buyer")
            sendCrystal(warehouse_account, setup_account, crystal_amount, setup_nonce, RPCProvider)
            setup_nonce+=1


    if enabled_profit:
            if  refiller_max_buffer*10**18 < getJewelBalance(setup_account, RPCProvider):
                jewel_amount = int(profit_amount*10**18)
                sendJewel(profit_address, setup_account, jewel_amount, setup_nonce, RPCProvider)
                setup_nonce+=1
                tablesManager.profit_tracking.put_item(
                        Item={
                            "time_": str(time.time()),
                            "amount": str(profit_amount),
                            "from": setup_address,
                            "address": profit_address
                        }
                )
            if refiller_max_buffer*10**18 < getJewelBalance(trader_account, RPCProvider):
                jewel_amount = int(profit_amount*10**18)
                sendJewel(profit_address, trader_account, jewel_amount, trader_nonce, RPCProvider)
                trader_nonce+=1
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
        #sellAllItems(trader_account, RPCProvider)

    
    warehouse_heros = heroNumber(warehouse_account, RPCProvider)

    deployer_settings = tablesManager.autoplayer.get_item(Key={"key_": "deployer_settings"})["Item"]

    enabled_deployer = deployer_settings["enabled"]
    manager_address = deployer_settings["manager_address"]
    last_account_address = deployer_settings["last_account"]
    gas_fill_amount = int(deployer_settings["gas_fill_amount"])

    target_accounts = tablesManager.managers.get_item(Key={"address_": manager_address})["Item"]["target_accounts"]
    current_accounts = len(tablesManager.accounts.scan(
            FilterExpression="pay_to = :manager_",
            ExpressionAttributeValues={
                ":manager_": manager_address,
            })["Items"])
    
    if not enabled_deployer: return "Deployer is disabled"
    last_account = get_account(tablesManager, secret, last_account_address, RPCProvider.w3)
    last_acc_jewel_balance = getJewelBalance(last_account, RPCProvider)
    last_acc_hero_number = heroNumber(last_account, RPCProvider)
    if 18 <= last_acc_hero_number and last_acc_jewel_balance != 0:
        if int(current_accounts) >= int(target_accounts): return "Target accounts reached"
        if 18 > warehouse_heros: return "Warehouse does not have enought heros"
        print("Last account has 18 heros and jewel balance")
        print("creating new account")
        new_account = createETHAddress()
        saveEncryption(tablesManager, secret, new_account["address"], new_account["private_key"], manager_address)
        deployed_account = get_account(tablesManager, secret, new_account["address"], RPCProvider.w3)
        print(f"New account created: {new_account['address']}")
        tablesManager.autoplayer.update_item(
                Key={"key_": "deployer_settings"},
                UpdateExpression="SET last_account = :account",
                ExpressionAttributeValues={":account": new_account["address"]}
        )
    else:
        if 18-last_acc_hero_number > warehouse_heros: return "Warehouse does not have enought heros"
        deployed_account = last_account
    
    hero_number = heroNumber(deployed_account, RPCProvider)
    jewel_balance = getJewelBalance(deployed_account, RPCProvider)

    print(f"Account has {hero_number} heros")
    logger.info(f"Account has {hero_number} heros")

    print(f"Account has {jewel_balance} jewel")
    logger.info(f"Account has {jewel_balance} jewel")

    if 18 <= hero_number and jewel_balance != 0:
        return "Account is already deployed"
    if jewel_balance == 0:
        print("Adding Gas")
        logger.info("Adding Gas")
        fillGas(deployed_account, setup_account, gas_fill_amount*10**18, setup_nonce, RPCProvider)
        setup_nonce+=1
        print(f"Filled gas to account {deployed_account.address}")
        logger.info(f"Filled gas to account {deployed_account.address}")
    if 18 <= hero_number:
        print("Account already has 18 heros")
        logger.info("Account already has 18 heros")
    else:
        amount = min(18-hero_number, warehouse_heros)
        print("Getting heros from warehouse")
        logger.info("Getting heros from warehouse")
        sendHeros(deployed_account, warehouse_account, amount, warehouse_nonce, RPCProvider)

    return "Done"