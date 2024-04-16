import requests

from core.wallet import *
from pathlib import Path
from helpers import *
from get_info import *
from constants import *
from chain_commander import *


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
        key_status_pair = getBLSKeysStatus([owner_address])
        if key_status_pair is None:
            return "no bls keys on this owner"
        for key, status in key_status_pair.items():
            if key == self.public_address():
                return status

    # is using /validator/statistics route
    def get_state(self) -> str:
        force_reset_validator_statistics()

        # sometimes it needs a second until cache is resetting
        time.sleep(1)

        response = requests.get(f"{DEFAULT_PROXY}/validator/statistics")
        response.raise_for_status()
        parsed = response.json()

        general_data = parsed.get("data")
        general_statistics = general_data.get("statistics")
        key_data = general_statistics.get(self.public_address())
        if key_data is None:
            return "Key not present in validator/statistics"
        else:
            status = key_data.get("validatorStatus")
            return status

    # using getOwner vm-query
    def belongs_to(self, address: str) -> bool:
        owner = getOwner([self.public_address()])
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