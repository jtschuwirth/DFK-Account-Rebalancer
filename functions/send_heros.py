import requests
import json

itemsJson = open("items_data/items_dfkchain.json")
items = json.load(itemsJson)

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

def sendHero(account, sender, heroId, sender_nonce, w3):
    tx = w3.eth.contract(address=items["Heroes"], abi=ERC721ABI).functions.transferFrom(sender.address, account.address, int(heroId)).build_transaction({
        "from": sender.address,
        "nonce": sender_nonce,
    })
    tx["gas"] = int(w3.eth.estimate_gas(tx))
    tx["maxFeePerGas"] = w3.toWei(50, 'gwei')
    tx["maxPriorityFeePerGas"] = w3.toWei(2, "gwei")
    signed_tx = w3.eth.account.sign_transaction(tx, sender.key)
    hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = w3.toHex(hash)

def sendHeros(account, sender, amount, sender_nonce, w3):
    nonce = sender_nonce
    c = amount
    heros = getAccountHeros(sender)
    if c > len(heros): 
        print("Not enough heros")
        return
    for hero in heros:
        sendHero(account, sender, hero["id"], nonce, w3)
        print("Sent hero " + str(hero["id"]) + " to " + account.address)
        nonce+=1
        c-=1
        if c == 0:
            break


