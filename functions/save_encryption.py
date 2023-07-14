from functions.data import f
import boto3
import os
from dotenv import load_dotenv

load_dotenv()


def init_table():
    my_session = boto3.session.Session(
            aws_access_key_id=os.environ.get("ACCESS_KEY"),
            aws_secret_access_key=os.environ.get("SECRET_KEY"),
            region_name = "us-east-1",
        )

    return my_session.resource('dynamodb').Table("dfk-autoplayer-accounts")

table = init_table()

def saveAccountData(table, user, key, pay_to):
    table.put_item(Item={
            "address_": user, 
            "key_": key,
            "pay_to": pay_to,
            "enabled_manager": True,
            "enabled_quester": True,
        })
    
def saveEncryption(user, key, pay_to):
    items = table.query(
            KeyConditionExpression="address_ = :address_",
            ExpressionAttributeValues={
                ":address_": user,
            })["Items"]
    if len(items) == 0:
        encoded_key = f.encrypt(key.encode()).decode()
        saveAccountData(table, user, encoded_key, pay_to)

