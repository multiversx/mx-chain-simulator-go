import requests
import json

from config import *
from get_info import *
from constants import *
import time



def SetEgldToAddress(egld_ammount, erd_address):
    details = {
        'address': f'{erd_address}',
        'balance': f'{egld_ammount}'
    }

    details_list = [details]
    json_structure = json.dumps(details_list)
    req = requests.post(DEFAULT_PROXY + "/simulator/set-state", data=json_structure)

    return req.text


def addBlocks(nr_of_blocks):
    req = requests.post(DEFAULT_PROXY + f"/simulator/generate-blocks/{nr_of_blocks}")
    return req.text


def addBlocksUntilEpochReached(epoch_to_be_reached: int):
    req = requests.post(DEFAULT_PROXY + f"/simulator/generate-blocks-until-epoch-reached/{str(epoch_to_be_reached)}")
    return req.text


def addBlocksUntilTxSucceeded(tx_hash) -> str:
    print("Checking: ", tx_hash)
    counter = 0

    while counter < MAX_NR_OF_BLOCKS_UNTIL_TX_SHOULD_BE_EXECUTED:
        addBlocks(1)

        time.sleep(WAIT_UNTIL_API_REQUEST_IN_SEC)
        if getStatusOfTx(tx_hash) == "pending":
            counter += 1
        else:
            print("Tx fully executed after", counter, " blocks.")
            return getStatusOfTx(tx_hash)


def is_chain_online() -> bool:
    flag = False

    while not flag:
        time.sleep(1)
        try:
            response = requests.get("http://localhost:8085/network/status/0")
            print(response)
            flag = True
        except requests.exceptions.ConnectionError:
            print("not jet")

    return flag


def force_reset_validator_statistics():
    req = requests.post(DEFAULT_PROXY + f"/simulator/force-reset-validator-statistics")
    print(req.text)

    return req.text


def addKey(private_keys: list) -> str:

    post_body = {
        "privateKeysBase64": private_keys
    }

    json_structure = json.dumps(post_body)
    req = requests.post(DEFAULT_PROXY + f"/simulator/add-keys", data=json_structure)

    return req.text

