import base64

import requests
from config import *
from helpers import *
from multiversx_sdk_core import Address
import json


def getBalance(address):
    req = requests.get(DEFAULT_PROXY + f"/address/{address}")

    balance = req.text
    balance = balance.split('"balance":')
    balance = balance[1].split(',')
    balance = balance[0].replace('"', "")

    return balance


def getPublicAddressFromPem(pem: Path):
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
    delegation_contract_address_as_bech32 = ""
    req = requests.get(DEFAULT_PROXY + f"/transaction/{tx_hash}?withResults=True")

    response = req.text
    response = response.split('"data":')
    for element in response:
        element = element.split('"')

        if len(element) > 1:
            try:
                conversion_to_hex = base64ToHex(element[1])
                if checkResponseDataStructureForDelegationContractAddress(conversion_to_hex):
                    delegation_contract_address = conversion_to_hex.split("@6f6b@")
                    delegation_contract_address = delegation_contract_address[1].replace("'", "")

                    delegation_contract_address_as_bech32 = Address.from_hex(delegation_contract_address,
                                                                             "erd").to_bech32()

            except:
                continue

    return delegation_contract_address_as_bech32


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
