from decimal import Decimal
import json
import time
import math
from eth_account import Account
import secrets
from functions.classes.APIService import APIService

from functions.classes.RPCProvider import RPCProvider

ERC20Json = open("abi/ERC20.json")
ERC20ABI = json.load(ERC20Json)

ERC721Json = open("abi/ERC721.json")
ERC721ABI = json.load(ERC721Json)

RouterJson = open("abi/UniswapV2Router02.json")
RouterABI = json.load(RouterJson)

ERC20Json = open("abi/ERC20.json")
ERC20ABI = json.load(ERC20Json)


def getCrystalBalance(account, apiService: APIService, rpcProvider: RPCProvider):
    contract = rpcProvider.w3.eth.contract(address= apiService.tokens["Crystal"].address, abi=ERC20ABI)
    return int(contract.functions.balanceOf(account.address).call())

def getJewelBalance(account, rpcProvider: RPCProvider):
    if rpcProvider.chain == "dfk":
        return int(rpcProvider.w3.eth.get_balance(account.address))
    else:
        return 0


def sendJewel(payout_account, account, amount, rpcProvider: RPCProvider):
    tx = {
        "from": account.address,
        "to": payout_account,
        "value": amount,
        "nonce": account.nonce,
        "chainId": rpcProvider.chainId
    }
    gas = rpcProvider.w3.eth.estimate_gas(tx)
    tx["gas"] = gas
    tx["gasPrice"] = rpcProvider.w3.to_wei(50, 'gwei')
    signed_tx = rpcProvider.w3.eth.account.sign_transaction(tx, account.key)
    hash = rpcProvider.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = rpcProvider.w3.to_hex(hash)

def sendCrystal(account, manager, amount, apiService: APIService, rpcProvider: RPCProvider):
    itemContract = rpcProvider.w3.eth.contract(address=apiService.tokens["Crystal"].address, abi=ERC20ABI)
    tx = itemContract.functions.transfer(
        account.address,
        amount,
    ).build_transaction({
        "from": manager.address,
        "nonce": account.nonce,
    })
    tx["gas"] = int(rpcProvider.w3.eth.estimate_gas(tx))
    tx["maxFeePerGas"] = rpcProvider.w3.to_wei(50, 'gwei')
    tx["maxPriorityFeePerGas"] = rpcProvider.w3.to_wei(2, "gwei")
    signed_tx = rpcProvider.w3.eth.account.sign_transaction(tx, manager.key)
    hash = rpcProvider.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = rpcProvider.w3.to_hex(hash)
    rpcProvider.w3.eth.wait_for_transaction_receipt(hash)

def buyCrystal(account, amount, expected_cost, apiService: APIService, rpcProvider: RPCProvider):
    RouterContract = rpcProvider.w3.eth.contract(address=apiService.contracts["Router"]["address"], abi=RouterABI)
    tx = RouterContract.functions.swapETHForExactTokens(
        amount,
        [apiService.tokens["Jewel"].address, apiService.tokens["Crystal"].address],
        account.address,
        int(time.time()+60)
        
    ).build_transaction({
        "from": account.address,
        "nonce": account.nonce,
        "value": expected_cost
    })
    tx["gas"] = int(rpcProvider.w3.eth.estimate_gas(tx))
    tx["maxFeePerGas"] = rpcProvider.w3.to_wei(50, 'gwei')
    tx["maxPriorityFeePerGas"] = rpcProvider.w3.to_wei(3, "gwei")
    signed_tx = rpcProvider.w3.eth.account.sign_transaction(tx, account.key)
    hash = rpcProvider.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = rpcProvider.w3.to_hex(hash)
    rpcProvider.w3.eth.wait_for_transaction_receipt(hash)

def getCrystalPriceJewel(apiService: APIService, rpcProvider: RPCProvider):
    RouterContract = rpcProvider.w3.eth.contract(address=apiService.contracts["Router"]["address"], abi=RouterABI)
    try:
        price = RouterContract.functions.getAmountsOut(1*10**18, [apiService.tokens["Crystal"].address, apiService.tokens["Jewel"].address]).call()[1]
        price = price/(10**18)
    except Exception as e:
        print(e)
        price = 0
    return price

def heroNumber(account, apiService: APIService, rpcProvider: RPCProvider):
    contract = rpcProvider.w3.eth.contract(address= apiService.contracts["Heroes"]["address"], abi=ERC721ABI)
    return int(contract.functions.balanceOf(account.address).call())

def createETHAddress():
    priv = secrets.token_hex(32)
    private_key = "0x" + priv
    acct = Account.from_key(private_key)
    return {"address": acct.address, "private_key": private_key}

def fillGas(account, manager, amount, rpcProvider: RPCProvider):
    tx = {
        "from": manager.address,
        "to": account.address,
        "value": amount,
        "nonce": account.nonce,
        "chainId": rpcProvider.chainId
    }
    gas = rpcProvider.w3.eth.estimate_gas(tx)
    tx["gas"] = gas
    tx["gasPrice"] = rpcProvider.w3.to_wei(50, 'gwei')
    signed_tx = rpcProvider.w3.eth.account.sign_transaction(tx, manager.key)
    hash = rpcProvider.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = rpcProvider.w3.to_hex(hash)
    rpcProvider.w3.eth.wait_for_transaction_receipt(hash)

def sellItemFromLiquidity(account, amount, token, expected_cost, apiService: APIService, rpcProvider: RPCProvider):
    RouterContract = rpcProvider.w3.eth.contract(address=apiService.contracts["Router"]["address"], abi=RouterABI)
    tx = RouterContract.functions.swapExactTokensForETH(
        amount,
        expected_cost,
        [token.address, apiService.tokens["Jewel"].address],
        account.address,
        int(time.time()+60)
        
    ).build_transaction({
        "from": account.address,
        "nonce": account.nonce
    })
    tx["gas"] = int(rpcProvider.w3.eth.estimate_gas(tx))
    tx["maxFeePerGas"] = rpcProvider.w3.to_wei(50, 'gwei')
    tx["maxPriorityFeePerGas"] = rpcProvider.w3.to_wei(3, "gwei")
    signed_tx = rpcProvider.w3.eth.account.sign_transaction(tx, account.key)
    hash = rpcProvider.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = rpcProvider.w3.to_hex(hash)
    rpcProvider.w3.eth.wait_for_transaction_receipt(hash)

def localGetAmountOut(amountIn, reserves):
    reserve_output = reserves["base_reserve"]
    reserve_input = reserves["token_reserve"]
    return math.floor(((Decimal(amountIn)*Decimal(997) * Decimal(reserve_output)) / (Decimal(reserve_input)*Decimal(1000) + Decimal(amountIn)*Decimal(997)))*Decimal(.99))

def checkAllowance(account, token, address, abi, rpcProvider):
    contract = rpcProvider.w3.eth.contract(address= token.address, abi=abi)
    if int(contract.functions.allowance(account.address, address).call()) == 0:
        return True
    else: 
        return False
    
def addAllowance(account, token, address, abi, rpcProvider):
    contract = rpcProvider.w3.eth.contract(address= token.address, abi=abi)
    tx = contract.functions.approve(address, 115792089237316195423570985008687907853269984665640564039457584007913129639935).build_transaction({
        "from": account.address,
        "nonce": account.nonce,
    })
    tx["gas"] = int(rpcProvider.w3.eth.estimate_gas(tx))
    tx["maxFeePerGas"] = rpcProvider.w3.to_wei(50, 'gwei')
    tx["maxPriorityFeePerGas"] = rpcProvider.w3.to_wei(2, "gwei")
    signed_tx = rpcProvider.w3.eth.account.sign_transaction(tx, account.key)
    hash = rpcProvider.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = rpcProvider.w3.to_hex(hash)
    rpcProvider.w3.eth.wait_for_transaction_receipt(hash)