# config.py
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

mongo_uri  = os.getenv("MONGO_DB")
secret_key = os.getenv("ENCRYPTION_KEY")

if not secret_key:
    print("Error: ENCRYPTION_KEY is missing from .env")

# Create client ONCE
client = MongoClient(mongo_uri)

# db_name is the actual database object
db_name   = client[os.getenv("DB_NAME")] #without client db doesnt get recognised!!

# These stay as plain strings — used as keys into db_name
kyc_col   = os.getenv("KYC")
vault_col = os.getenv("GOVT_DOC")