from decimal import Decimal
import json
import time
import math
from eth_account import Account
import secrets

itemsJson = open("data/items.json")
items = json.load(itemsJson)

decimalsJson = open("data/decimals.json")
decimals_data = json.load(decimalsJson)

contractsJson = open("data/contracts.json")
contracts = json.load(contractsJson)

ERC20Json = open("abi/ERC20.json")
ERC20ABI = json.load(ERC20Json)

ERC721Json = open("abi/ERC721.json")
ERC721ABI = json.load(ERC721Json)

RouterAddress = "0x3C351E1afdd1b1BC44e931E12D4E05D6125eaeCa"
RouterJson = open("abi/UniswapV2Router02.json")
RouterABI = json.load(RouterJson)

ERC20Json = open("abi/ERC20.json")
ERC20ABI = json.load(ERC20Json)


def getCrystalBalance(account, RPCProvider):
    contract = RPCProvider.w3.eth.contract(address= items["Crystal"][RPCProvider.chain], abi=ERC20ABI)
    return int(contract.functions.balanceOf(account.address).call())

def getJewelBalance(account, RPCProvider):
    if RPCProvider.chain == "dfk":
        return int(RPCProvider.w3.eth.get_balance(account.address))
    else:
        return 0


def sendJewel(payout_account, account, amount, nonce, RPCProvider):
    tx = {
        "from": account.address,
        "to": payout_account,
        "value": amount,
        "nonce": nonce,
        "chainId": RPCProvider.chainId
    }
    gas = RPCProvider.w3.eth.estimate_gas(tx)
    tx["gas"] = gas
    tx["gasPrice"] = RPCProvider.w3.to_wei(50, 'gwei')
    signed_tx = RPCProvider.w3.eth.account.sign_transaction(tx, account.key)
    hash = RPCProvider.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = RPCProvider.w3.to_hex(hash)

def sendCrystal(account, manager, amount, nonce, RPCProvider):
    itemContract = RPCProvider.w3.eth.contract(address=items["Crystal"][RPCProvider.chain], abi=ERC20ABI)
    tx = itemContract.functions.transfer(
        account.address,
        amount,
    ).build_transaction({
        "from": manager.address,
        "nonce": nonce,
    })
    tx["gas"] = int(RPCProvider.w3.eth.estimate_gas(tx))
    tx["maxFeePerGas"] = RPCProvider.w3.to_wei(50, 'gwei')
    tx["maxPriorityFeePerGas"] = RPCProvider.w3.to_wei(2, "gwei")
    signed_tx = RPCProvider.w3.eth.account.sign_transaction(tx, manager.key)
    hash = RPCProvider.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = RPCProvider.w3.to_hex(hash)
    RPCProvider.w3.eth.wait_for_transaction_receipt(hash)

def buyCrystal(account, amount, expected_cost, nonce, RPCProvider):
    RouterContract = RPCProvider.w3.eth.contract(address=RouterAddress, abi=RouterABI)
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
    tx["gas"] = int(RPCProvider.w3.eth.estimate_gas(tx))
    tx["maxFeePerGas"] = RPCProvider.w3.to_wei(50, 'gwei')
    tx["maxPriorityFeePerGas"] = RPCProvider.w3.to_wei(3, "gwei")
    signed_tx = RPCProvider.w3.eth.account.sign_transaction(tx, account.key)
    hash = RPCProvider.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = RPCProvider.w3.to_hex(hash)
    RPCProvider.w3.eth.wait_for_transaction_receipt(hash)

def getCrystalPriceJewel(RPCProvider):
    RouterContract = RPCProvider.w3.eth.contract(address=RouterAddress, abi=RouterABI)
    try:
        price = RouterContract.functions.getAmountsOut(1*10**18, [items["Crystal"][RPCProvider.chain], items["Jewel"][RPCProvider.chain]]).call()[1]
        price = price/(10**18)
    except Exception as e:
        print(e)
        price = 0
    return price

def heroNumber(account, RPCProvider):
    contract = RPCProvider.w3.eth.contract(address= contracts["Heroes"][RPCProvider.chain], abi=ERC721ABI)
    return int(contract.functions.balanceOf(account.address).call())

def createETHAddress():
    priv = secrets.token_hex(32)
    private_key = "0x" + priv
    acct = Account.from_key(private_key)
    return {"address": acct.address, "private_key": private_key}

def fillGas(account, manager, amount, nonce, RPCProvider):
    tx = {
        "from": manager.address,
        "to": account.address,
        "value": amount,
        "nonce": nonce,
        "chainId": RPCProvider.chainId
    }
    gas = RPCProvider.w3.eth.estimate_gas(tx)
    tx["gas"] = gas
    tx["gasPrice"] = RPCProvider.w3.to_wei(50, 'gwei')
    signed_tx = RPCProvider.w3.eth.account.sign_transaction(tx, manager.key)
    hash = RPCProvider.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = RPCProvider.w3.to_hex(hash)
    RPCProvider.w3.eth.wait_for_transaction_receipt(hash)

def sellItemFromLiquidity(account, amount, token, expected_cost, RPCProvider):
    RouterContract = RPCProvider.w3.eth.contract(address=contracts["RouterAddress"][RPCProvider.chain], abi=RouterABI)
    tx = RouterContract.functions.swapExactTokensForETH(
        amount,
        expected_cost,
        [token.address, items["Jewel"][RPCProvider.chain]],
        account.address,
        int(time.time()+60)
        
    ).build_transaction({
        "from": account.address,
        "nonce": account.nonce
    })
    tx["gas"] = int(RPCProvider.w3.eth.estimate_gas(tx))
    tx["maxFeePerGas"] = RPCProvider.w3.to_wei(50, 'gwei')
    tx["maxPriorityFeePerGas"] = RPCProvider.w3.to_wei(3, "gwei")
    signed_tx = RPCProvider.w3.eth.account.sign_transaction(tx, account.key)
    hash = RPCProvider.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = RPCProvider.w3.to_hex(hash)
    RPCProvider.w3.eth.wait_for_transaction_receipt(hash)

def localGetAmountOut(amountIn, reserves):
    reserve_output = reserves["base_reserve"]
    reserve_input = reserves["token_reserve"]
    return math.floor(((Decimal(amountIn)*Decimal(997) * Decimal(reserve_output)) / (Decimal(reserve_input)*Decimal(1000) + Decimal(amountIn)*Decimal(997)))*Decimal(.99))

def checkAllowance(account, token, address, abi, RPCProvider):
    contract = RPCProvider.w3.eth.contract(address= token.address, abi=abi)
    if int(contract.functions.allowance(account.address, address).call()) == 0:
        return True
    else: 
        return False
    
def addAllowance(account, token, address, abi, RPCProvider):
    contract = RPCProvider.w3.eth.contract(address= token.address, abi=abi)
    tx = contract.functions.approve(address, 115792089237316195423570985008687907853269984665640564039457584007913129639935).build_transaction({
        "from": account.address,
        "nonce": account.nonce,
    })
    tx["gas"] = int(RPCProvider.w3.eth.estimate_gas(tx))
    tx["maxFeePerGas"] = RPCProvider.w3.to_wei(50, 'gwei')
    tx["maxPriorityFeePerGas"] = RPCProvider.w3.to_wei(2, "gwei")
    signed_tx = RPCProvider.w3.eth.account.sign_transaction(tx, account.key)
    hash = RPCProvider.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = RPCProvider.w3.to_hex(hash)
    RPCProvider.w3.eth.wait_for_transaction_receipt(hash)