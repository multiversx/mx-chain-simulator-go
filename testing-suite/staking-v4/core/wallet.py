from pathlib import Path
from config import *
import requests
import json
from multiversx_sdk_network_providers import ProxyNetworkProvider
from multiversx_sdk_wallet import UserSigner
from multiversx_sdk_core import Address
from multiversx_sdk_network_providers import accounts
from helpers import *
from constants import *


class Wallet:
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

    def get_balance(self) -> int:
        req = requests.get(DEFAULT_PROXY + f"/address/{self.public_address()}")

        balance = req.text
        balance = balance.split('"balance":')
        balance = balance[1].split(',')
        balance = balance[0].replace('"', "")

        return balance

    def set_balance(self, egld_ammount):
        details = {
            'address': f'{self.public_address()}',
            'balance': f'{egld_ammount}'
        }

        details_list = [details]
        json_structure = json.dumps(details_list)
        req = requests.post(DEFAULT_PROXY + "/simulator/set-state", data=json_structure)

        return req.text

    def get_signer(self) -> UserSigner:
        return UserSigner.from_pem_file(self.path)

    def get_address(self) -> Address:
        return Address.from_bech32(self.public_address())

    def get_account(self):
        return proxy_default.get_account(self.get_address())
