from cryptography.fernet import Fernet

class Account:
    def __init__(self, account) -> None:
        self.account = account
        self.address = account.address
        self.key = account.key
        self.nonce = 0
    
    def update_nonce(self, RPCProvider):
        self.nonce = RPCProvider.w3.eth.get_transaction_count(self.address, "pending")

def get_account(tables_manager, Secret, address, RPCProvider):
    f = Fernet(Secret.value["dfk-secret-key"].encode())
    key = tables_manager.accounts.query(
            KeyConditionExpression="address_ = :address_",
            ExpressionAttributeValues={
                ":address_": address,
            })["Items"][0]["key_"]
    decrypted_key = f.decrypt(key.encode()).decode()
    return Account(RPCProvider.w3.eth.account.from_key(decrypted_key))