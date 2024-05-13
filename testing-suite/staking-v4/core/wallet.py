
from config import *
import requests
import json
from multiversx_sdk_wallet import UserSigner
from multiversx_sdk_core import Address

from utils.logger import logger


class Wallet:
    def __init__(self, path: Path) -> None:
        self.path = path
        logger.info(f"Wallet initialized with path: {self.path}")

    def public_address(self) -> str:
        with open(self.path) as f:
            lines = f.readlines()

        for line in lines:
            if "BEGIN" in line:
                line = line.split(" ")
                address = line[-1].replace("-----", "").strip()
                return address

    def get_balance(self) -> int:
        address = self.public_address()
        logger.info(f"Fetching balance for address: {address}")
        response = requests.get(f"{DEFAULT_PROXY}/address/{address}/balance")
        response.raise_for_status()
        parsed = response.json()

        general_data = parsed.get("data")
        balance = general_data.get("balance")
        logger.info(f"Retrieved balance: {balance} for address: {address}")

        return balance

    def set_balance(self, egld_amount):
        address = self.public_address()
        logger.info(f"Setting balance for address: {address} to {egld_amount}")
        details = {
            'address': address,
            'balance': egld_amount
        }

        details_list = [details]
        json_structure = json.dumps(details_list)
        req = requests.post(f"{DEFAULT_PROXY}/simulator/set-state", data=json_structure)
        logger.info(f"Set balance request status: {req.status_code}")

        return req.text

    def get_signer(self) -> UserSigner:
        logger.info("Creating UserSigner from PEM file.")
        return UserSigner.from_pem_file(self.path)

    def get_address(self) -> Address:
        address = self.public_address()
        return Address.from_bech32(address)

    def get_account(self):
        account = proxy_default.get_account(self.get_address())
        logger.info(f"Retrieved account details for: {account.address.to_bech32()}")
        return account