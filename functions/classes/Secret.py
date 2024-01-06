from aiohttp import ClientError
import boto3
import json

class Secret:
    def __init__(self, secret) -> None:
        self.value = secret

def get_secret(secret_name):
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name="us-east-1",
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']
    return Secret(json.loads(secret))
