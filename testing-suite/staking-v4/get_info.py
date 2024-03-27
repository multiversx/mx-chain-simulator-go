import base64

import requests
from config import *
from helpers import *
from multiversx_sdk_core import Address
import json
import time

def getBalance(address):
    req = requests.get(DEFAULT_PROXY + f"/address/{address}")

    balance = req.text
    balance = balance.split('"balance":')
    balance = balance[1].split(',')
    balance = balance[0].replace('"', "")

    return balance


def getPublicAddressFromPem(pem: Path) -> str:
    f = open(pem)
    lines = f.readlines()
    for line in lines:
        if "BEGIN" in line:
            line = line.split(" ")
            address = line[-1].replace("-----", "")
            if "\n" in address:
                address = address.replace("\n", "")
            break

    return address


def getStatusOfTx(tx_hash: str):
    req = requests.get(DEFAULT_PROXY + f"/transaction/{tx_hash}/process-status")

    status = req.text
    status = status.split('"status":')
    status = status[1].split('"')

    return status[1]


def getDelegationContractAddressFromTx(tx_hash):
    delegation_contract_address = ""
    req = requests.get(DEFAULT_PROXY + f"/transaction/{tx_hash}?withResults=True")

    response = req.text
    response = response.split('"logs":')
    response = response[1].split("identifier")
    for element in response:
        if "delegate" in element:
            element = element.split('"topics":["')
            element = element[1].split(",")
            element = element[4].split('"')
            for _ in element:
                if len(_) > 3:
                    delegation_contract_address = _

    delegation_contract_address = base64ToHex(delegation_contract_address)
    delegation_contract_address = Address.from_hex(delegation_contract_address, "erd").to_bech32()

    return  delegation_contract_address


def getBLSKeysStatus(owner_public_key_in_hex: list[str]):
    key_status_pair = {}
    key_status_temp_list = []

    post_body = {
        "scAddress": "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l",
        "funcName": "getBlsKeysStatus",
        "args": owner_public_key_in_hex
    }

    json_structure = json.dumps(post_body)
    req = requests.post(DEFAULT_PROXY + "/vm-values/query", data=json_structure)

    # get returnData
    response = req.text

    if '"returnData":null' in response:
        return None

    response = response.split('"returnData":')
    response = response[1].split('"returnCode"')
    response = response[0].split('"')
    for element in response:
        if len(element) > 3:
            key_status_temp_list.append(element)

    # convert all elements from list to hex and add to final dict:
    for i in range(0, len(key_status_temp_list), 2):
        bls_decoded = base64ToHex(key_status_temp_list[i])
        status_decoded = base64ToString(key_status_temp_list[i + 1])

        key_status_pair[bls_decoded] = status_decoded

    return key_status_pair


def checkIfErrorIsPresentInTx(error, tx_hash) -> bool:
    flag = False
    error = stringToBase64(error)

    req = requests.get(DEFAULT_PROXY + f"/transaction/{tx_hash}?withResults=True")
    response = req.text

    if error.decode() in response:
        flag = True

    return flag
