import json
from functions.classes.APIService import APIService
from functions.classes.RPCProvider import RPCProvider

from functions.classes.Token import Token

pairContractJson = open("abi/UniswapPair.json")
pairABI = json.load(pairContractJson)

def getReserves(token: Token, apiService: APIService, RPCProvider: RPCProvider):
    if token.name not in apiService.pairs:
        return {
            "token_reserve": 0,
            "base_reserve": 0
        }
    pair_address = apiService.pairs[token.name]["address"]
    PairContract = RPCProvider.w3.eth.contract(address=pair_address, abi=pairABI)
    tokens_reserve = PairContract.functions.getReserves().call()
    if token.decimals == 0 or token.decimals == 3:
        return {
            "token_reserve": min(tokens_reserve[0], tokens_reserve[1]),
            "base_reserve": max(tokens_reserve[0], tokens_reserve[1])
        }
    return {
        "token_reserve": tokens_reserve[0],
        "base_reserve": tokens_reserve[1]
    }


