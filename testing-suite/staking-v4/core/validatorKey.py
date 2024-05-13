import requests
import time
from core.wallet import *
from pathlib import Path
from caching import force_reset_validator_statistics
from network_provider.get_validator_info import get_bls_key_status
from network_provider.get_validator_info import get_owner
from config import DEFAULT_PROXY, OBSERVER_META


class ValidatorKey:
    def __init__(self, path: Path) -> None:
        self.path = path
        logger.info(f"ValidatorKey initialized with path: {path}")

    def public_address(self) -> str:
        f = open(self.path)
        lines = f.readlines()
        for line in lines:
            if "BEGIN" in line:
                line = line.split(" ")
                address = line[-1].replace("-----", "")
                if "\n" in address:
                    address = address.replace("\n", "")
                break
        return address

    # is using vm-query with "getBlsKeysStatus" function
    def get_status(self, owner_address: str):
        owner_address = Address.from_bech32(owner_address).to_hex()
        key_status_pair = get_bls_key_status([owner_address])
        if key_status_pair is None:
            logger.warning("No status found for any keys")
            return None
        for key, status in key_status_pair.items():
            if key == self.public_address():
                logger.info(f"Status: {status} for BLS Key: {key} ")
                return status

    # is using /validator/statistics route
    def get_state(self):
        force_reset_validator_statistics()

        response = requests.get(f"{OBSERVER_META}/validator/statistics")
        response.raise_for_status()
        parsed = response.json()

        general_data = parsed.get("data")
        general_statistics = general_data.get("statistics")
        key_data = general_statistics.get(self.public_address())

        if key_data is None:
            logger.warning(f"No state data found for validator key: {key_data}")
            return None
        else:
            status = key_data.get("validatorStatus")
            logger.info(f"Validator status is: {status}")
            return status

    # is using /validator/auction
    def get_auction_state(self):
        logger.info(f"Resetting validator statistics before fetching auction state.")
        force_reset_validator_statistics()

        logger.info(f"Requesting auction state from {OBSERVER_META}/validator/auction.")
        response = requests.get(f"{OBSERVER_META}/validator/auction")
        response.raise_for_status()
        parsed = response.json()

        general_data = parsed.get("data")
        auction_list_data = general_data.get("auctionList")

        for list in auction_list_data:
            nodes_lists = list.get("nodes")
            for node_list in nodes_lists:
                if node_list.get("blsKey") == self.public_address():
                    state = node_list.get("qualified")
                    if state:
                        logger.info(f"BLS key {self.public_address()} is qualified in the auction.")
                        return "qualified"
                    else:
                        logger.info(f"BLS key {self.public_address()} is unqualified in the auction.")
                        return "unqualified"
                else:
                    logger.info(f"No auction data found for BLS key {self.public_address()}.")
                    return None

    # using getOwner vm-query
    def belongs_to(self, address: str) -> bool:
        owner = get_owner([self.public_address()])
        if owner == address:
            logger.info(f"Checked ownership: True for address: {address}")
            return True
        else:
            logger.info(f"Checked ownership: False for address: {address}")
            return False

    def get_private_key(self) -> str:
        private_key = ""

        f = open(self.path)
        lines = f.readlines()
        for line in lines:
            if not "BEGIN" in line and not "END" in line:
                private_key += line
        if "\n" in private_key:
            private_key = private_key.replace("\n", "")
        logger.debug(f"Private key retrieved for {self.path}")
        return private_key