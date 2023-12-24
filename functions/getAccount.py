from cryptography.fernet import Fernet

def get_account(tables_manager, secret, address, w3):
    f = Fernet(secret["dfk-secret-key"].encode())
    key = tables_manager.accounts.query(
            KeyConditionExpression="address_ = :address_",
            ExpressionAttributeValues={
                ":address_": address,
            })["Items"][0]["key_"]
    decrypted_key = f.decrypt(key.encode()).decode()
    return w3.eth.account.from_key(decrypted_key)