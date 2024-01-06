import json
from gnosis.eth import EthereumClient
from gnosis.eth.contracts import get_erc20_contract
from functions.classes.APIService import APIService
from functions.classes.Account import Account
from functions.classes.RPCProvider import RPCProvider
from functions.classes.Token import Token
from functions.getReserves import getReserves

from functions.utils import addAllowance, checkAllowance, localGetAmountOut, sellItemFromLiquidity

ERC20Json = open("abi/ERC20.json")
ERC20ABI = json.load(ERC20Json)

def sellAllItems(account: Account, apiService: APIService, rpcProvider: RPCProvider):
    ethereum_client = EthereumClient(rpcProvider.url)

    erc20_contract = get_erc20_contract(ethereum_client.w3, apiService.tokens["Crystal"].address)
    tokens = []
    items_addresses = []
    for token in apiService.tokens.values():
        if token.name == "Jewel":
            continue
        elif token.name== "Crystal"  and rpcProvider.chain != "dfk":
            continue
        elif token.name == "Jade" and rpcProvider.chain != "klay":
             continue
        
        tokens.append(token)
        items_addresses.append(token.address)

    response = ethereum_client.batch_call_same_function(erc20_contract.functions.balanceOf(account.address), items_addresses)
    for i in range(len(response)):
        if response[i] > 0:  
            token = tokens[i]
            reserves = getReserves(token, rpcProvider)
            expected_cost = localGetAmountOut(response[i], reserves)

            if checkAllowance(account, token, apiService.contracts["Router"]["address"], ERC20ABI, rpcProvider):
                account.update_nonce(rpcProvider)
                addAllowance(account, token, apiService.contracts["Router"]["address"], ERC20ABI, rpcProvider)
            
            print(f"Selling {response[i]} {token.name} for {expected_cost / 10**18} Jewel on {rpcProvider.chain}")
            account.update_nonce(rpcProvider)
            sellItemFromLiquidity(
                account,
                response[i],
                token,
                expected_cost,
                rpcProvider
            )
    