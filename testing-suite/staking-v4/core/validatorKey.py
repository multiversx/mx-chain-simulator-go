import requests

import time
import urllib.request, json
import wget

from core.wallet import *
from pathlib import Path
from caching import force_reset_validator_statistics
from get_infos.get_validator_info import get_bls_key_status
from get_infos.get_validator_info import get_owner
from config import DEFAULT_PROXY, OBSERVER_META


class ValidatorKey:
    def __init__(self, path: Path) -> None:
        self.path = path

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
    def get_status(self, owner_address: str) -> str:
        owner_address = Address.from_bech32(owner_address).to_hex()
        key_status_pair = get_bls_key_status([owner_address])
        if key_status_pair is None:
            return "no bls keys on this owner"
        for key, status in key_status_pair.items():
            if key == self.public_address():
                return status

    # is using /validator/statistics route
    def get_state(self):

        force_reset_validator_statistics()

        # sometimes it needs few seconds until cache is resetting
        time.sleep(1)

        response = requests.get(f"{OBSERVER_META}/validator/statistics")
        response.raise_for_status()
        parsed = response.json()

        general_data = parsed.get("data")
        general_statistics = general_data.get("statistics")
        key_data = general_statistics.get(self.public_address())

        if key_data is None:
            return None
        else:
            status = key_data.get("validatorStatus")
            return status

    # is using /validator/auction
    def get_auction_state(self):
        force_reset_validator_statistics()

        # sometimes it needs few seconds until cache is resetting
        time.sleep(1)

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
                        return "qualified"
                    else:
                        return "unqualified"


        # using getOwner vm-query
    def belongs_to(self, address: str) -> bool:
        owner = get_owner([self.public_address()])
        if owner == address:
            return True
        else:
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

        return private_key