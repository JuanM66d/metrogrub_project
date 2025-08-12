import looker_sdk
import json
import os


LOOKER_HOST = os.getenv("LOOKER_HOST")
LOOKERSDK_API_VERSION = "4.0"

LOOKERSDK_CLIENT_ID = os.getenv("LOOKERSDK_CLIENT_ID")
LOOKERSDK_CLIENT_SECRET = os.getenv("LOOKERSDK_CLIENT_SECRET")


sdk = looker_sdk.init40()

