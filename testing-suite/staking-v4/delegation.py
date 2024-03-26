from multiversx_sdk_wallet.validator_pem import ValidatorPEM
from multiversx_sdk_wallet.validator_signer import ValidatorSigner
from multiversx_sdk_core import Transaction
from multiversx_sdk_core import Address
from multiversx_sdk_core.transaction import TransactionComputer
from multiversx_sdk_network_providers import ProxyNetworkProvider
from multiversx_sdk_wallet import UserSigner
from get_info import *
from config import *
from helpers import *
from core.wallet import *


proxy_default = ProxyNetworkProvider(DEFAULT_PROXY)
proxy_config = proxy_default.get_network_config()


def createNewDelegationContract(owner: Wallet, AMOUNT="1250000000000000000000", SERVICE_FEE="00", DELEGATION_CAP="00") -> str:
    # compute tx
    tx = Transaction(sender=owner.get_address().to_bech32(),
                     receiver=SYSTEM_DELEGATION_MANAGER_CONTRACT,
                     nonce=owner.get_account().nonce,
                     gas_price=1000000000,
                     gas_limit=590000000,
                     chain_id=proxy_config.chain_id,
                     value=int(AMOUNT))

    tx.data = f"createNewDelegationContract@{DELEGATION_CAP}@{SERVICE_FEE}".encode()

    tx_comp = TransactionComputer()
    result_bytes = tx_comp.compute_bytes_for_signing(tx)

    signature = owner.get_signer().sign(result_bytes)
    tx.signature = signature

    # send tx
    tx_hash = proxy_default.send_transaction(tx)
    return tx_hash


def whitelistForMerge(old_owner: Wallet, new_owner: Wallet, delegation_sc_address: str) -> str:

    delegation_sc_address = Address.from_bech32(delegation_sc_address)

    # compute tx
    tx = Transaction(sender=old_owner.get_address().to_bech32(),
                     receiver=delegation_sc_address.to_bech32(),
                     nonce=old_owner.get_account().nonce,
                     gas_price=1000000000,
                     gas_limit=590000000,
                     chain_id=proxy_config.chain_id,
                     value=0)

    tx.data = f"whitelistForMerge@{new_owner.get_address().to_hex()}".encode()

    tx_comp = TransactionComputer()
    result_bytes = tx_comp.compute_bytes_for_signing(tx)

    signature = old_owner.get_signer().sign(result_bytes)
    tx.signature = signature

    # send tx
    tx_hash = proxy_default.send_transaction(tx)
    return tx_hash


def mergeValidatorToDelegationWithWhitelist(new_owner: Wallet, delegation_sc_address: str):

    delegation_sc_address_as_hex = Address.from_bech32(delegation_sc_address).to_hex()

    # compute tx
    tx = Transaction(sender=new_owner.get_address().to_bech32(),
                     receiver=SYSTEM_DELEGATION_MANAGER_CONTRACT,
                     nonce=new_owner.get_account().nonce,
                     gas_price=1000000000,
                     gas_limit=590000000,
                     chain_id=proxy_config.chain_id,
                     value=0)

    tx.data = f"mergeValidatorToDelegationWithWhitelist@{delegation_sc_address_as_hex}".encode()

    tx_comp = TransactionComputer()
    result_bytes = tx_comp.compute_bytes_for_signing(tx)

    signature = new_owner.get_signer().sign(result_bytes)
    tx.signature = signature

    # send tx
    tx_hash = proxy_default.send_transaction(tx)
    return tx_hash




