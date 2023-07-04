from functions.data import account_table, settings_table, tracking_table
from functions.getMarketHeros import getMarketHeros
from functions.provider import get_provider, get_account
from functions.buyHero import buyHero
from functions.getCrystalBalance import getCrystalBalance

w3 = get_provider("dfk")

def handler(event, context):
    scan_response = account_table.scan(
            FilterExpression="warehouse = :warehouse",
            ExpressionAttributeValues={
                ":warehouse": True
            })
    settings = settings_table.get_item(Key={"key_": "buyer_settings"})["Item"]
    enabled = settings["enabled"]
    max_price = settings["max_price"]
    if not enabled: return "Buyer is disabled"
    account = get_account(scan_response["Items"][0]["address_"], w3)
    nonce = w3.eth.get_transaction_count(account.address)
    heros_to_buy = getMarketHeros(10, max_price)
    if len(heros_to_buy) == 0: return "No heros to buy"
    for hero in heros_to_buy:
        try:
            if getCrystalBalance(account, w3) < hero["price"]: return "Not enough crystals"
            buyHero(account, hero["id"], hero["price"], nonce, w3)
            tracking_table.put_item(Item={"heroId": hero["id"], "price": str(hero["price"]/10**18)})
            print(f"Hero {hero['id']} bought for {hero['price']} crystals")
            nonce+=1
        except Exception as e:
            print(e)
            pass
    return "Done"