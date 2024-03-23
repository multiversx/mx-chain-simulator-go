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


def createNewDelegationContract(owner_pem: Path, AMOUNT="1250000000000000000000", SERVICE_FEE="00", DELEGATION_CAP="00") -> str:
    proxy_default = ProxyNetworkProvider(DEFAULT_PROXY)
    proxy_config = proxy_default.get_network_config()

    # load needed data from owner pem
    wallet_public_address = getPublicAddressFromPem(owner_pem)
    wallet_address = Address.from_bech32(wallet_public_address)
    wallet_signer = UserSigner.from_pem_file(owner_pem)
    wallet_account = proxy_default.get_account(wallet_address)

    # compute tx
    tx = Transaction(sender=wallet_address.to_bech32(),
                     receiver=SYSTEM_DELEGATION_MANAGER_CONTRACT,
                     nonce=wallet_account.nonce,
                     gas_price=1000000000,
                     gas_limit=590000000,
                     chain_id=proxy_config.chain_id,
                     value=int(AMOUNT))

    tx.data = f"createNewDelegationContract@{DELEGATION_CAP}@{SERVICE_FEE}".encode()

    tx_comp = TransactionComputer()
    result_bytes = tx_comp.compute_bytes_for_signing(tx)

    signature = wallet_signer.sign(result_bytes)
    tx.signature = signature

    # send tx
    tx_hash = proxy_default.send_transaction(tx)
    return tx_hash


