import json
from gnosis.eth import EthereumClient
from gnosis.eth.contracts import get_erc20_contract
from functions.classes.Account import Account
from functions.classes.Token import Token
from functions.getReserves import getReserves

from functions.utils import addAllowance, checkAllowance, localGetAmountOut, sellItemFromLiquidity

itemsJson = open("data/items.json")
items = json.load(itemsJson)

decimalsJson = open("data/decimals.json")
decimals_data = json.load(decimalsJson)

contractsJson = open("data/contracts.json")
contracts = json.load(contractsJson)

ERC20Json = open("abi/ERC20.json")
ERC20ABI = json.load(ERC20Json)

def sellAllItems(account, RPCProvider):
    ethereum_client = EthereumClient(RPCProvider.url)

    erc20_contract = get_erc20_contract(ethereum_client.w3, items["Crystal"][RPCProvider.chain])
    items_names = []
    items_addresses = []
    for item in items:
        if item == "Jewel":
            continue
        elif item == "Crystal"  and RPCProvider.chain != "dfk":
            continue
        elif item == "Jade" and RPCProvider.chain != "klay":
             continue
        
        items_names.append(item)
        items_addresses.append(items[item][RPCProvider.chain])

    response = ethereum_client.batch_call_same_function(erc20_contract.functions.balanceOf(account.address), items_addresses)
    for i in range(len(response)):
        if response[i] > 0:  
            token = Token(
                items_names[i],
                RPCProvider.chain,
                None
            )
            account = Account(account.key, RPCProvider)
            reserves = getReserves(token, RPCProvider)
            expected_cost = localGetAmountOut(response[i], reserves)

            if checkAllowance(account, token, contracts["RouterAddress"][RPCProvider.chain], ERC20ABI, RPCProvider):
                account.update_nonce(RPCProvider)
                addAllowance(account, token, contracts["RouterAddress"][RPCProvider.chain], ERC20ABI, RPCProvider)
            
            print(f"Selling {response[i]} {items_names[i]} for {expected_cost / 10**18} Jewel on {RPCProvider.chain}")
            account.update_nonce(RPCProvider)
            sellItemFromLiquidity(
                account,
                response[i],
                token,
                expected_cost,
                RPCProvider
            )
    