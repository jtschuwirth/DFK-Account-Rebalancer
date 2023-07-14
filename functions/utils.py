import json
import time
from eth_account import Account
import secrets
chainId= 53935

itemsJson = open("items_data/items_dfkchain.json")
items = json.load(itemsJson)

decimalsJson = open("items_data/decimals.json")
decimals_data = json.load(decimalsJson)

ERC20Json = open("abi/ERC20.json")
ERC20ABI = json.load(ERC20Json)

ERC721Json = open("abi/ERC721.json")
ERC721ABI = json.load(ERC721Json)

RouterAddress = "0x3C351E1afdd1b1BC44e931E12D4E05D6125eaeCa"
RouterJson = open("abi/UniswapV2Router02.json")
RouterABI = json.load(RouterJson)

ERC20Json = open("abi/ERC20.json")
ERC20ABI = json.load(ERC20Json)

itemsJson = open("items_data/items_dfkchain.json")
items = json.load(itemsJson)

def getCrystalBalance(account, w3):
    contract = w3.eth.contract(address= items["Crystal"], abi=ERC20ABI)
    return int(contract.functions.balanceOf(account.address).call())

def getJewelBalance(account, w3):
    return int(w3.eth.get_balance(account.address))


def sendCrystal(account, manager, amount, nonce, w3):
    itemContract = w3.eth.contract(address=items["Crystal"], abi=ERC20ABI)
    tx = itemContract.functions.transfer(
        account.address,
        amount,
    ).build_transaction({
        "from": manager.address,
        "nonce": nonce,
    })
    tx["gas"] = int(w3.eth.estimate_gas(tx))
    tx["maxFeePerGas"] = w3.toWei(50, 'gwei')
    tx["maxPriorityFeePerGas"] = w3.toWei(2, "gwei")
    signed_tx = w3.eth.account.sign_transaction(tx, manager.key)
    hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = w3.toHex(hash)
    w3.eth.wait_for_transaction_receipt(hash)

def buyCrystal(account, amount, expected_cost, nonce, w3):
    RouterContract = w3.eth.contract(address=RouterAddress, abi=RouterABI)
    tx = RouterContract.functions.swapETHForExactTokens(
        amount,
        [items["Jewel"], items["Crystal"]],
        account.address,
        int(time.time()+60)
        
    ).build_transaction({
        "from": account.address,
        "nonce": nonce,
        "value": expected_cost
    })
    tx["gas"] = int(w3.eth.estimate_gas(tx))
    tx["maxFeePerGas"] = w3.toWei(50, 'gwei')
    tx["maxPriorityFeePerGas"] = w3.toWei(3, "gwei")
    signed_tx = w3.eth.account.sign_transaction(tx, account.key)
    hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = w3.toHex(hash)
    w3.eth.wait_for_transaction_receipt(hash)

def getCrystalPriceJewel(w3):
    RouterContract = w3.eth.contract(address=RouterAddress, abi=RouterABI)
    try:
        price = RouterContract.functions.getAmountsOut(1*10**18, [items["Crystal"], items["Jewel"]]).call()[1]
        price = price/(10**18)
    except Exception as e:
        print(e)
        price = 0
    return price

def heroNumber(account, w3):
    contract = w3.eth.contract(address= items["Heroes"], abi=ERC721ABI)
    return int(contract.functions.balanceOf(account.address).call())

def createETHAddress():
    priv = secrets.token_hex(32)
    private_key = "0x" + priv
    acct = Account.from_key(private_key)
    return {"address": acct.address, "private_key": private_key}

def fillGas(account, manager, amount, nonce, w3):
    tx = {
        "from": manager.address,
        "to": account.address,
        "value": amount,
        "nonce": nonce,
        "chainId": chainId
    }
    gas = w3.eth.estimate_gas(tx)
    tx["gas"] = gas
    tx["gasPrice"] = w3.toWei(50, 'gwei')
    signed_tx = w3.eth.account.sign_transaction(tx, manager.key)
    hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = w3.toHex(hash)
    w3.eth.wait_for_transaction_receipt(hash)