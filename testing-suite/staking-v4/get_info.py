import base64

import requests
from config import *
from helpers import *
from multiversx_sdk_core import Address
import json
import time
from constants import *


def get_status_of_tx(tx_hash: str) -> str:
    response = requests.get(f"{DEFAULT_PROXY}/transaction/{tx_hash}/process-status")
    response.raise_for_status()
    parsed = response.json()

    if "transaction not found" in response.text:
        return "expired"

    general_data = parsed.get("data")
    status = general_data.get("status")
    return status


def get_delegation_contract_address_from_tx(tx_hash):

    response = requests.get(f"{DEFAULT_PROXY}/transaction/{tx_hash}?withResults=True")
    response.raise_for_status()
    parsed = response.json()

    general_data = parsed.get("data")
    transaction_data = general_data.get("transaction")
    logs_data = transaction_data.get("logs")
    events_data = logs_data.get("events")
    first_set_of_events = events_data[0]
    topics = first_set_of_events.get("topics")
    delegation_contract_address = topics[1]

    delegation_contract_address = base64_to_hex(delegation_contract_address)
    delegation_contract_address = Address.from_hex(delegation_contract_address, "erd").to_bech32()

    return delegation_contract_address


def get_bls_key_status(owner_public_key_in_hex: list[str]):
    key_status_pair = {}

    post_body = {
        "scAddress": "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l",
        "funcName": "getBlsKeysStatus",
        "args": owner_public_key_in_hex
    }

    json_structure = json.dumps(post_body)
    response = requests.post(f"{DEFAULT_PROXY}/vm-values/query", data=json_structure)
    response.raise_for_status()
    parsed = response.json()

    if '"returnData":null' in response.text:
        return None

    general_data = parsed.get("data")
    tx_response_data = general_data.get("data")
    key_status_temp_list = tx_response_data.get("returnData")

    # convert all elements from list to hex and add to final dict:
    for i in range(0, len(key_status_temp_list), 2):
        bls_decoded = base64_to_hex(key_status_temp_list[i])
        status_decoded = base64_to_string(key_status_temp_list[i + 1])

        key_status_pair[bls_decoded] = status_decoded

    return key_status_pair


def get_owner(public_validator_key: list[str]) -> str:

    post_body = {
        "scAddress": STAKING_CONTRACT,
        "funcName": "getOwner",
        "caller": VALIDATOR_CONTRACT,
        "args": public_validator_key
    }

    json_structure = json.dumps(post_body)
    response = requests.post(f"{DEFAULT_PROXY}/vm-values/query", data=json_structure)
    response.raise_for_status()
    parsed = response.json()

    if '"returnMessage":"owner address is nil"' in response.text:
        return "validatorKey not staked"

    general_data = parsed.get("data")
    tx_response_data = general_data.get("data")
    address_list = tx_response_data.get("returnData")
    address = address_list[0]

    address = base64_to_hex(address)
    address = Address.from_hex(address, "erd").to_bech32()

    return address


def check_if_error_is_present_in_tx(error, tx_hash) -> bool:
    flag = False
    error_bytes = string_to_base64(error)

    req = requests.get(f"{DEFAULT_PROXY}/transaction/{tx_hash}?withResults=True")
    response = req.text

    if error_bytes.decode() in response:
        flag = True

    if error in response:
        flag = True

    return flag


def get_total_staked(owner: str):
    address_in_hex = Address.from_bech32(owner).to_hex()
    post_body = {
        "scAddress": VALIDATOR_CONTRACT,
        "funcName": "getTotalStaked",
        "args": [address_in_hex]
    }

    json_structure = json.dumps(post_body)
    response = requests.post(f"{DEFAULT_PROXY}/vm-values/query", data=json_structure)
    response.raise_for_status()
    parsed = response.json()

    general_data = parsed.get("data")
    tx_response_data = general_data.get("data")
    total_staked_list = tx_response_data.get("returnData")
    total_staked = total_staked_list[0]

    total_staked = base64_to_string(total_staked)
    return total_staked
