import requests
import json

from config import *
from get_info import *
from constants import *
import time


def send_egld_to_address(egld_amount, erd_address):
    details = {
        'address': f'{erd_address}',
        'balance': f'{egld_amount}'
    }

    details_list = [details]
    json_structure = json.dumps(details_list)
    response = requests.post(f"{DEFAULT_PROXY}/simulator/set-state", data=json_structure)
    response.raise_for_status()

    return response.text


def add_blocks(nr_of_blocks):
    req = requests.post(f"{DEFAULT_PROXY}/simulator/generate-blocks/{nr_of_blocks}")
    return req.text


def add_blocks_until_epoch_reached(epoch_to_be_reached: int):
    req = requests.post(f"{DEFAULT_PROXY}/simulator/generate-blocks-until-epoch-reached/{str(epoch_to_be_reached)}")
    return req.text


def add_blocks_until_tx_fully_executed(tx_hash) -> str:
    print("Checking: ", tx_hash)
    counter = 0

    while counter < MAX_NUM_OF_BLOCKS_UNTIL_TX_SHOULD_BE_EXECUTED:
        add_blocks(1)

        time.sleep(WAIT_UNTIL_API_REQUEST_IN_SEC)
        if get_status_of_tx(tx_hash) == "pending":
            counter += 1
        else:
            print("Tx fully executed after", counter, " blocks.")
            return get_status_of_tx(tx_hash)


def is_chain_online() -> bool:
    flag = False

    while not flag:
        time.sleep(1)
        try:
            response = requests.get(f"{DEFAULT_PROXY}/network/status/0")
            print(response)
            flag = True
        except requests.exceptions.ConnectionError:
            print("Chain not started jet")

    return flag


def force_reset_validator_statistics():
    req = requests.post(f"{DEFAULT_PROXY}/simulator/force-reset-validator-statistics")
    print(req.text)

    return req.text


def add_key(private_keys: list) -> str:
    post_body = {
        "privateKeysBase64": private_keys
    }

    json_structure = json.dumps(post_body)
    req = requests.post(f"{DEFAULT_PROXY}/simulator/add-keys", data=json_structure)

    return req.text
