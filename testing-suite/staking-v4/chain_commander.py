import requests
import json

from config import *


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