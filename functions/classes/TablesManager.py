import os
import boto3

class TablesManager:
    def __init__(self, prod) -> None:
        if not prod:
            session = boto3.session.Session(
                aws_access_key_id=os.environ.get("ACCESS_KEY"),
                aws_secret_access_key=os.environ.get("SECRET_KEY"),
                region_name = "us-east-1",
            )
        else:
            session = boto3.session.Session(
                region_name = "us-east-1",
            )

        self.accounts = session.resource('dynamodb').Table("dfk-autoplayer-accounts")
        self.autoplayer = session.resource('dynamodb').Table("dfk-autoplayer")
        self.profit_tracker = session.resource('dynamodb').Table("dfk-profit-tracker")
        self.managers = session.resource('dynamodb').Table("dfk-autoplayer-managers")
        self.settings = session.resource('dynamodb').Table("dfk-autoplayer")
        self.trades = session.resource('dynamodb').Table("dfk-trading-trades")
        self.active_orders = session.resource('dynamodb').Table("dfk-trading-active-orders")
        


    

