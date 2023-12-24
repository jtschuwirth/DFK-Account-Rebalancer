import json

itemsJson = open("data/items.json")
items = json.load(itemsJson)

decimalsJson = open("data/decimals.json")
decimals_data = json.load(decimalsJson)

pairsJson = open("data/pairs.json")
pairs = json.load(pairsJson)

pairContractJson = open("abi/UniswapPair.json")
pairABI = json.load(pairContractJson)

def getReserves(token, RPCProvider):
    pair_address = pairs["Jewel"][token.name]
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


