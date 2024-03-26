from core.wallet import *
from pathlib import Path
from helpers import *
from get_info import *


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
    def get_status(self, owner: Wallet) -> str:
        key_status_pair = getBLSKeysStatus([owner.get_address().to_hex()])
        for key, status in key_status_pair.items():
            if key == self.public_address():
                return status

    def belongs_to(self, owner: Wallet) -> bool:
        flag = False
        key_status_pair = getBLSKeysStatus([owner.get_address().to_hex()])
        for key in key_status_pair.keys():
            if key == self.public_address():
                flag = True
        return flag

    # TODO: get_state , to be using validator-statistics

