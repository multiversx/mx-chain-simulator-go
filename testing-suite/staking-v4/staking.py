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
from core.validatorKey import *

# def stake(walletKey_pem: Path, validatorKeys_pem: list[Path]):
#     proxy_default = ProxyNetworkProvider(DEFAULT_PROXY)
#     proxy_config = proxy_default.get_network_config()
#
#     # load needed data from walletKey.pem
#     wallet_public_address = getPublicAddressFromPem(walletKey_pem)
#     wallet_address = Address.from_bech32(wallet_public_address)
#     wallet_signer = UserSigner.from_pem_file(walletKey_pem)
#     wallet_account = proxy_default.get_account(wallet_address)
#
#     # nr of nodes staked
#     nr_of_nodes_staked = len(validatorKeys_pem)
#     nr_of_nodes_staked = stringToHex(nr_of_nodes_staked)
#
#     # load needed data for stake transactions signatures
#     stake_signature_and_public_key = ''
#     for key in validatorKeys_pem:
#         pem_file = ValidatorPEM.from_file(key)
#         public_key = getPublicAddressFromPem(key)
#
#         validator_signer = ValidatorSigner(pem_file.secret_key)
#         signed_message = validator_signer.sign(wallet_address.pubkey).hex()
#
#         stake_signature_and_public_key += f"@{public_key}@{signed_message}"
#
#     # compute value of tx
#     amount = str(len(validatorKeys_pem) * 2500) + "000000000000000000"
#
#     # create transaction
#     tx = Transaction(sender=wallet_address.to_bech32(),
#                      receiver=SYSTEM_STAKING_CONTRACT,
#                      nonce=wallet_account.nonce,
#                      gas_price=1000000000,
#                      gas_limit=590000000,
#                      chain_id=proxy_config.chain_id,
#                      value=int(amount))
#
#     tx.data = f"stake@{nr_of_nodes_staked}{stake_signature_and_public_key}".encode()
#
#     # prepare signature
#     tx_comp = TransactionComputer()
#     result_bytes = tx_comp.compute_bytes_for_signing(tx)
#
#     signature = wallet_signer.sign(result_bytes)
#     tx.signature = signature
#
#     # send tx
#     tx_hash = proxy_default.send_transaction(tx)
#
#     return tx_hash


def stake(wallet: Wallet, validatorKeys: list[ValidatorKey]):

    # nr of nodes staked
    nr_of_nodes_staked = len(validatorKeys)
    nr_of_nodes_staked = stringToHex(nr_of_nodes_staked)

    # load needed data for stake transactions signatures
    stake_signature_and_public_key = ''
    for key in validatorKeys:
        pem_file = ValidatorPEM.from_file(key.path)
        public_key = key.public_address()

        validator_signer = ValidatorSigner(pem_file.secret_key)
        signed_message = validator_signer.sign(wallet.get_address().pubkey).hex()

        stake_signature_and_public_key += f"@{public_key}@{signed_message}"

    # compute value of tx
    amount = str(len(validatorKeys) * 2500) + "000000000000000000"

    # create transaction
    tx = Transaction(sender=wallet.get_address().to_bech32(),
                     receiver=SYSTEM_STAKING_CONTRACT,
                     nonce=wallet.get_account().nonce,
                     gas_price=1000000000,
                     gas_limit=590000000,
                     chain_id=proxy_config.chain_id,
                     value=int(amount))

    tx.data = f"stake@{nr_of_nodes_staked}{stake_signature_and_public_key}".encode()

    # prepare signature
    tx_comp = TransactionComputer()
    result_bytes = tx_comp.compute_bytes_for_signing(tx)

    signature = wallet.get_signer().sign(result_bytes)
    tx.signature = signature

    # send tx
    tx_hash = proxy_default.send_transaction(tx)

    return tx_hash
