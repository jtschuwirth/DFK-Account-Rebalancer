import requests
import json

from functions.classes.APIService import APIService
from functions.classes.Account import Account
from functions.classes.RPCProvider import RPCProvider

graph_url = "https://defi-kingdoms-community-api-gateway-co06z8vi.uc.gateway.dev/graphql"
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0'
}

ERC721Json = open("abi/ERC721.json")
ERC721ABI = json.load(ERC721Json)

def getAccountHeros(account):
    query = """
          query($owner: String, $profession: String) {
              heroes(orderBy: id, where: {
                owner: $owner,
                network: "dfk",
                salePrice: null,
                professionStr: $profession,
              }) {
                  id
              }
          }
      """
     
    variables = {
        "profession": "mining",
        "owner": account.address,
    }

    return requests.post(graph_url, json={"query":query, "variables":variables}, headers=headers).json()["data"]["heroes"]

def sendHero(account: Account, sender: Account, heroId, apiService: APIService, rpcProvider: RPCProvider):
    tx =  rpcProvider.w3.eth.contract(address=apiService.contracts["Heroes"]["address"], abi=ERC721ABI).functions.transferFrom(sender.address, account.address, int(heroId)).build_transaction({
        "from": sender.address,
        "nonce": sender.nonce,
    })
    tx["gas"] = int( rpcProvider.w3.eth.estimate_gas(tx))
    tx["maxFeePerGas"] =  rpcProvider.w3.to_wei(50, 'gwei')
    tx["maxPriorityFeePerGas"] = rpcProvider.w3.to_wei(2, "gwei")
    signed_tx =  rpcProvider.w3.eth.account.sign_transaction(tx, sender.key)
    hash =  rpcProvider.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash =  rpcProvider.w3.to_hex(hash)

def sendHeros(account, sender, amount, apiService: APIService, rpcProvider: RPCProvider):
    c = amount
    heros = getAccountHeros(sender)
    if c > len(heros): 
        print("Not enough heros")
        return
    for hero in heros:
        sender.update_nonce(rpcProvider)
        sendHero(account, sender, hero["id"], apiService, rpcProvider)
        print("Sent hero " + str(hero["id"]) + " to " + account.address)
        c-=1
        if c == 0:
            break


