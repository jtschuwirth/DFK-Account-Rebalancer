from functions.data import account_table, settings_table, tracking_table, init_managers_table
from functions.getMarketHeros import getMarketHeros
from functions.provider import get_provider, get_account
from functions.buyHero import buyHero
from functions.utils import getCrystalBalance, getJewelBalance, sendCrystal, buyCrystal, getCrystalPriceJewel, heroNumber, createETHAddress, fillGas
from functions.save_encryption import saveEncryption
from functions.send_heros import sendHeros
import time

w3 = get_provider("dfk")

def handler(event, context):
    managers_table = init_managers_table()
    warehouse_address = account_table.scan(
            FilterExpression="warehouse = :warehouse",
            ExpressionAttributeValues={
                ":warehouse": True
            })["Items"][0]["address_"]
    buyer_settings = settings_table.get_item(Key={"key_": "buyer_settings"})["Item"]
    enabled_buyer = buyer_settings["enabled"]
    max_price = buyer_settings["max_price"]
    enabled_refiller = buyer_settings["refiller"]
    setup_address = buyer_settings["refiller_address"]
    refiller_min_buffer = float(buyer_settings["refiller_min_buffer"])
    buyer_min_buffer = float(buyer_settings["buyer_min_buffer"])
    buyer_refill_amount = float(buyer_settings["buyer_refill_amount"])
    setup_account = get_account(setup_address, w3)
    setup_nonce = w3.eth.get_transaction_count(setup_account.address)

    warehouse_account = get_account(warehouse_address, w3)
    warehouse_nonce = w3.eth.get_transaction_count(warehouse_account.address)
    if enabled_refiller:
        if refiller_min_buffer*10**18 < getJewelBalance(setup_account, w3) and getCrystalBalance(warehouse_account, w3) < buyer_min_buffer*10**18:
            crystal_value = getCrystalPriceJewel(w3) 
            crystal_amount = int(buyer_refill_amount*10**18)
            expected_cost = int(crystal_amount*crystal_value*1.05)
            print("Refilling buyer account")
            print(f"Buying {buyer_refill_amount} crystals")
            buyCrystal(setup_account, crystal_amount, expected_cost, setup_nonce, w3)
            setup_nonce+=1
            print(f"Sending {buyer_refill_amount} crystals to buyer")
            sendCrystal(warehouse_account, setup_account, crystal_amount, setup_nonce, w3)
            setup_nonce+=1

    if not enabled_buyer: return "Buyer is disabled"
    heros_to_buy = getMarketHeros(10, max_price)
    if len(heros_to_buy) != 0:
        for hero in heros_to_buy:
            try:
                if getCrystalBalance(warehouse_account, w3) < hero["price"]: return "Not enough crystals"
                buyHero(warehouse_account, hero["id"], hero["price"], warehouse_nonce, w3)
                tracking_table.put_item(Item={"heroId_": str(hero["id"]), "price": str(hero["price"]/10**18), "time_": str(int(time.time()))})
                print(f"Hero {hero['id']} bought for {hero['price']/10*18} crystals")
                warehouse_nonce+=1
            except Exception as e:
                print(e)
                pass
    
    warehouse_heros = heroNumber(warehouse_account, w3)

    deployer_settings = settings_table.get_item(Key={"key_": "deployer_settings"})["Item"]

    enabled_deployer = deployer_settings["enabled"]
    manager_address = deployer_settings["manager_address"]
    last_account_address = deployer_settings["last_account"]
    gas_fill_amount = int(deployer_settings["gas_fill_amount"])

    target_accounts = managers_table.get_item(Key={"address_": manager_address})["Item"]["target_accounts"]
    current_accounts = len(account_table.scan(
            FilterExpression="pay_to = :manager_",
            ExpressionAttributeValues={
                ":manager_": manager_address,
            })["Items"])
    
    if not enabled_deployer: return "Deployer is disabled"
    last_account = get_account(last_account_address, w3)
    last_acc_jewel_balance = getJewelBalance(last_account, w3)
    last_acc_hero_number = heroNumber(last_account, w3)
    if 18 <= last_acc_hero_number and last_acc_jewel_balance != 0:
        if int(current_accounts) >= int(target_accounts): return "Target accounts reached"
        if 18 > warehouse_heros: return "Warehouse does not have enought heros"
        print("Last account has 18 heros and jewel balance")
        print("creating new account")
        new_account = createETHAddress()
        saveEncryption(new_account["address"], new_account["private_key"], manager_address)
        deployed_account = get_account(new_account["address"], w3)
        print(f"New account created: {new_account['address']}")
        settings_table.update_item(
                Key={"key_": "deployer_settings"},
                UpdateExpression="SET last_account = :account",
                ExpressionAttributeValues={":account": new_account["address"]}
        )
    else:
        if 18-last_acc_hero_number > warehouse_heros: return "Warehouse does not have enought heros"
        deployed_account = last_account
    
    hero_number = heroNumber(deployed_account, w3)
    jewel_balance = getJewelBalance(deployed_account, w3)
    print(f"Account has {hero_number} heros")
    print(f"Account has {jewel_balance} jewel")

    if 18 <= hero_number and jewel_balance != 0:
        return "Account is already deployed"
    if jewel_balance == 0:
        print("Adding Gas")
        fillGas(deployed_account, setup_account, gas_fill_amount*10**18, setup_nonce, w3)
        setup_nonce+=1
        print(f"Filled gas to account {deployed_account.address}")
    if 18 <= hero_number:
        print("Account already has 18 heros")
    else:
        amount = min(18-hero_number, warehouse_heros)
        print("Getting heros from warehouse")
        sendHeros(deployed_account, warehouse_account, amount, warehouse_nonce, w3)

    return "Done"