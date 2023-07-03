from web3 import Web3
from web3.middleware import geth_poa_middleware
from functions.data import f, account_table

def get_provider(network):
    if network == "dfk":
        rpc_url = "https://subnets.avax.network/defi-kingdoms/dfk-chain/rpc"
    elif network== "kla":
        rpc_url = "https://public-en-cypress.klaytn.net"
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    w3.clientVersion
    return w3

def get_account(address, w3):
    key = account_table.query(
            KeyConditionExpression="address_ = :address_",
            ExpressionAttributeValues={
                ":address_": address,
            })["Items"][0]["key_"]
    decrypted_key = f.decrypt(key.encode()).decode()
    return w3.eth.account.from_key(decrypted_key)
