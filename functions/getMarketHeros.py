import requests
graph_url = "https://defi-kingdoms-community-api-gateway-co06z8vi.uc.gateway.dev/graphql"
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0'
}

def getMarketHeros(amount, max_price):
    query = """
          query($max_price: String, $profession: String) {
              heroes(orderBy: salePrice, where: {
                  network: "dfk",
                  salePrice_not: null,
                  salePrice_lte:$max_price,
                  professionStr: $profession,
                  privateAuctionProfile: null
              }) {
                  id
                  salePrice
              }
          }
      """
     
    variables = {
        "max_price": str(max_price*10**18),
        "profession": "mining",
    }
     
    response = requests.post(graph_url, json={"query":query, "variables":variables}, headers=headers)
    c=0
    total_cost = 0
    heros = []
    for hero in response.json()["data"]["heroes"]:
        if c==amount: break
        total_cost += int(hero["salePrice"])
        heros.append({"id": int(hero["id"]), "price": int(hero["salePrice"])})
        c+=1
    return heros