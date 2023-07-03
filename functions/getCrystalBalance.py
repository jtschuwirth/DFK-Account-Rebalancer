import json

ERC20Json = open("abi/ERC20.json")
ERC20ABI = json.load(ERC20Json)

itemsJson = open("items_data/items_dfkchain.json")
items = json.load(itemsJson)

def getCrystalBalance(account, w3):
    contract = w3.eth.contract(address= items["Crystal"], abi=ERC20ABI)
    return int(contract.functions.balanceOf(account.address).call())