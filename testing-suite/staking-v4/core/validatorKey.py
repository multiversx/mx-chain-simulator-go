from core.wallet import *
from pathlib import Path
from helpers import *
from get_info import *
from constants import *


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
    def get_status(self, address: str) -> str:
        address = Address.from_bech32(address).to_hex()
        key_status_pair = getBLSKeysStatus([address])
        if key_status_pair is None:
            return "no bls keys on this owner"
        for key, status in key_status_pair.items():
            if key == self.public_address():
                return status

    # using getOwner vm-query
    def belongs_to(self, address: str) -> bool:
        owner = getOwner([self.public_address()])
        if owner == address:
            return True
        else:
            return False

    # TODO: get_state , to be using validator-statistics
