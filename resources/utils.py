
import json
from dotenv import load_dotenv


def fetch_endpoint_ocid(key):
    content=json.load(open("config/endpoints.json"))
    return str(content[key])


def return_keys_from_endpoint_config() -> object:
    """

    :rtype: object
    """
    content = json.load(open("config/endpoints.json"))
    list_keys = list(content.keys())
    list_keys.append("Custom")
    return list_keys


def load_env():
    try:
        load_dotenv("config/config.cfg")
    except Exception as error:
        print(f"Failed to load env {error}")





