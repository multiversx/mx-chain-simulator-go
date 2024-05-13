import json
import time

import requests
from config import DEFAULT_PROXY, OBSERVER_META
from constants import STAKING_CONTRACT
from constants import VALIDATOR_CONTRACT
from helpers import base64_to_hex
from helpers import base64_to_string
from multiversx_sdk_core import Address
from caching import force_reset_validator_statistics
from utils.logger import logger


def get_bls_key_status(owner_public_key_in_hex: list[str]):
    logger.info(f"Fetching BLS key status for public keys")
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
        logger.warning("No return data available for BLS keys status")
        return None

    general_data = parsed.get("data")
    tx_response_data = general_data.get("data")
    key_status_temp_list = tx_response_data.get("returnData")

    # convert all elements from list to hex and add to final dict:
    for i in range(0, len(key_status_temp_list), 2):
        bls_decoded = base64_to_hex(key_status_temp_list[i])
        status_decoded = base64_to_string(key_status_temp_list[i + 1])

        key_status_pair[bls_decoded] = status_decoded

    logger.info(f"Successfully retrieved BLS key statuses")
    return key_status_pair


def get_owner(public_validator_key: list[str]) -> str:
    logger.info(f"Fetching owner for public validator key")
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
        logger.warning("No owner address found for given validator key")
        return "validatorKey not staked"

    general_data = parsed.get("data")
    tx_response_data = general_data.get("data")
    address_list = tx_response_data.get("returnData")
    address = address_list[0]

    address = base64_to_hex(address)
    address = Address.from_hex(address, "erd").to_bech32()

    logger.info(f"Owner address successfully retrieved: {address}")
    return address


# using validator/statistics
def get_keys_state(keys: list) -> list[str]:
    logger.info("Fetching states for validator keys")
    states = []

    force_reset_validator_statistics()

    response = requests.get(f"{OBSERVER_META}/validator/statistics")
    response.raise_for_status()

    parsed = response.json()

    general_data = parsed.get("data")
    statistics = general_data.get("statistics")

    for key in keys:
        if not statistics.get(key) is None:
            key_data = statistics.get(key)
            state = key_data.get("validatorStatus")
            states.append(state)

    logger.info(f"Successfully retrieved states for {len(states)} keys")
    return states


def get_keys_from_validator_auction(isQualified=True) -> list[str]:
    logger.info(f"Fetching keys from validator auction with qualification status {isQualified}")

    keys = []

    force_reset_validator_statistics()

    response = requests.get(f"{OBSERVER_META}/validator/auction")
    response.raise_for_status()
    parsed = response.json()

    general_data = parsed.get("data")
    auction_list_data = general_data.get("auctionList")

    for list in auction_list_data:
        nodes_lists = list.get("nodes")
        for node_list in nodes_lists:
            if node_list.get("qualified") == isQualified:
                keys.append(node_list.get("blsKey"))

    logger.info(f"Successfully retrieved {len(keys)} qualified keys from validator auction")
    return keys


def get_keys_from_validator_statistics(needed_state: str) -> list[str]:
    logger.info(f"Fetching keys from validator statistics with needed state: {needed_state}")
    keys = []

    force_reset_validator_statistics()

    response = requests.get(f"{OBSERVER_META}/validator/statistics")
    response.raise_for_status()
    parsed = response.json()

    general_data = parsed.get("data")
    statistics = general_data.get("statistics")

    for dict in statistics:
        key_data = statistics.get(dict)
        state = key_data.get("validatorStatus")
        if state == needed_state:
            keys.append(dict)

    logger.info(f"Successfully retrieved {len(keys)} keys with state '{needed_state}' from validator statistics")
    return keys


