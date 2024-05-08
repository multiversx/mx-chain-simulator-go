from core.validatorKey import ValidatorKey
import requests
from chain_commander import add_blocks_until_epoch_reached, add_blocks
from config import proxy_default, DEFAULT_PROXY
import json


def add_key(keys: list[ValidatorKey]) -> str:
    private_keys = []
    for key in keys:
        private_keys.append(key.get_private_key())

    post_body = {
        "privateKeysBase64": private_keys
    }

    json_structure = json.dumps(post_body)
    req = requests.post(f"{DEFAULT_PROXY}/simulator/add-keys", data=json_structure)

    return req.text


def add_blocks_until_key_eligible(keys: list[ValidatorKey]) -> ValidatorKey:
    flag = False
    while not flag:
        for key in keys:
            if key.get_state() == "eligible":
                eligible_key = key
                print("eligible key found")
                flag = True

            else:
                print("no eligible key found , moving to next epoch...")
                current_epoch = proxy_default.get_network_status().epoch_number
                add_blocks_until_epoch_reached(current_epoch+1)
                add_blocks(3)

    return eligible_key