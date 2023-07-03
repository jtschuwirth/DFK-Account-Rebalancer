import json

HeroSaleAddress = "0xc390fAA4C7f66E4D62E59C231D5beD32Ff77BEf0"
HeroSaleJson = open("abi/HeroSale.json")
HeroSaleABI = json.load(HeroSaleJson)

def buyHero(account, heroId, heroPrice, nonce, w3):
    HeroSaleContract = w3.eth.contract(address=HeroSaleAddress, abi=HeroSaleABI)
    tx = HeroSaleContract.functions.bid(heroId, heroPrice).build_transaction({
        "from": account.address,
        "nonce": nonce
    })
    gas = int(w3.eth.estimate_gas(tx)*1.1)
    tx["gas"] = gas
    tx["maxFeePerGas"] = w3.toWei(50, 'gwei')
    tx["maxPriorityFeePerGas"] = w3.toWei(2, "gwei")
    signed_tx = w3.eth.account.sign_transaction(tx, account.key)
    hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = w3.toHex(hash)
    w3.eth.wait_for_transaction_receipt(hash)