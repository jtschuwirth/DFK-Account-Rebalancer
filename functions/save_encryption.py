from cryptography.fernet import Fernet

from functions.classes.Secret import Secret

def saveAccountData(table, user, key, pay_to):
    table.put_item(Item={
            "address_": user, 
            "key_": key,
            "pay_to": pay_to,
            "enabled_manager": True,
            "enabled_quester": True,
        })
    
def saveEncryption(tablesManager, secret: Secret, user, key, pay_to):
    f = Fernet(secret.value["dfk-secret-key"].encode())
    items = tablesManager.accounts.query(
            KeyConditionExpression="address_ = :address_",
            ExpressionAttributeValues={
                ":address_": user,
            })["Items"]
    if len(items) == 0:
        encoded_key = f.encrypt(key.encode()).decode()
        saveAccountData(tablesManager.accounts, user, encoded_key, pay_to)

