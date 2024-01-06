import os
from dotenv import load_dotenv
load_dotenv()

isProd = os.environ.get("PROD")=="true"
secretName=os.environ["DFK_SECRET_NAME"]