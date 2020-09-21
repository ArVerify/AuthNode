import os
from dotenv import load_dotenv

load_dotenv('.env')

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

ARWEAVE_KEYFILE = os.environ.get("ARWEAVE_KEYFILE", "arweave-keyfile.json")

FEE = float(os.environ.get("FEE", None))
