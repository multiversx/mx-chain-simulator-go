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
    def get_status(self, *arg) -> str:

        if isinstance(arg[0], Wallet):
            key_status_pair = getBLSKeysStatus([arg[0].get_address().to_hex()])
            if key_status_pair is None:
                return "no bls keys on this owner"
            for key, status in key_status_pair.items():
                if key == self.public_address():
                    return status

        if isinstance(arg[0], str):
            address = Address.from_bech32(arg[0]).to_hex()
            key_status_pair = getBLSKeysStatus([address])
            if key_status_pair is None:
                return "no bls keys on this owner"
            for key, status in key_status_pair.items():
                if key == self.public_address():
                    return status



    def belongs_to(self, *arg) -> bool:
        flag = False

        if isinstance(arg[0], Wallet):
            key_status_pair = getBLSKeysStatus([arg[0].get_address().to_hex()])
            if key_status_pair is None:
                return False
            for key in key_status_pair.keys():
                if key == self.public_address():
                    flag = True

        if isinstance(arg[0], str):
            address = Address.from_bech32(arg[0]).to_hex()
            key_status_pair = getBLSKeysStatus([address])
            if key_status_pair is None:
                return False
            for key in key_status_pair.keys():
                if key == self.public_address():
                    flag = True

        return flag


    # TODO: get_state , to be using validator-statistics
