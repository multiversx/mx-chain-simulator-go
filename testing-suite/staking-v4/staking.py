from multiversx_sdk_wallet.validator_pem import ValidatorPEM
from multiversx_sdk_wallet.validator_signer import ValidatorSigner
from multiversx_sdk_core import Transaction
from multiversx_sdk_core import Address
from multiversx_sdk_core.transaction import TransactionComputer
from multiversx_sdk_network_providers import ProxyNetworkProvider
from multiversx_sdk_wallet import UserSigner

from config import *
from helpers import *
from core.wallet import *
from core.validatorKey import ValidatorKey
from constants import *


def stake(wallet: Wallet, validatorKeys: list[ValidatorKey]):
    # nr of nodes staked
    nr_of_nodes_staked = len(validatorKeys)
    nr_of_nodes_staked = decimal_to_hex(nr_of_nodes_staked)

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
                     receiver=VALIDATOR_CONTRACT,
                     nonce=wallet.get_account().nonce,
                     gas_price=1000000000,
                     gas_limit=200000000,
                     chain_id=chain_id,
                     value=int(amount))

    tx.data = f"stake@{nr_of_nodes_staked}{stake_signature_and_public_key}".encode()

    # prepare signature
    tx_comp = TransactionComputer()
    result_bytes = tx_comp.compute_bytes_for_signing(tx)

    signature = wallet.get_signer().sign(result_bytes)
    tx.signature = signature

    # send tx
    tx_hash = proxy_default.send_transaction(tx)

    logger.info(f"Staking transaction sent, transaction hash: {tx_hash}")
    return tx_hash


def malicious_stake(wallet: Wallet, validatorKeys: list[ValidatorKey], AMOUNT_DEFICIT="0", TX_DATA_MANIPULATOR=False):
    # nr of nodes staked
    nr_of_nodes_staked = len(validatorKeys)
    nr_of_nodes_staked = decimal_to_hex(nr_of_nodes_staked)

    # load needed data for stake transactions signatures
    stake_signature_and_public_key = ''
    for key in validatorKeys:
        pem_file = ValidatorPEM.from_file(key.path)
        public_key = key.public_address()

        validator_signer = ValidatorSigner(pem_file.secret_key)
        signed_message = validator_signer.sign(wallet.get_address().pubkey).hex()

        stake_signature_and_public_key += f"@{public_key}@{signed_message}"

    # compute value of tx
    amount = int(str(len(validatorKeys) * 2500) + "000000000000000000") - int(AMOUNT_DEFICIT)

    # create transaction
    tx = Transaction(sender=wallet.get_address().to_bech32(),
                     receiver=VALIDATOR_CONTRACT,
                     nonce=wallet.get_account().nonce,
                     gas_price=1000000000,
                     gas_limit=200000000,
                     chain_id=chain_id,
                     value=int(amount))

    if TX_DATA_MANIPULATOR:
        data = f"{nr_of_nodes_staked}{stake_signature_and_public_key}"
        manipulated_data = replace_random_data_with_another_random_data(data)
        tx.data = f"stake@{manipulated_data}".encode()
    else:
        tx.data = f"stake@{nr_of_nodes_staked}{stake_signature_and_public_key}".encode()

    # prepare signature
    tx_comp = TransactionComputer()
    result_bytes = tx_comp.compute_bytes_for_signing(tx)

    signature = wallet.get_signer().sign(result_bytes)
    tx.signature = signature

    # send tx
    tx_hash = proxy_default.send_transaction(tx)

    logger.info(f"Malicious staking transaction sent, transaction hash: {tx_hash}")
    return tx_hash


def unStake(wallet: Wallet, validator_key: ValidatorKey) -> str:
    # create transaction
    tx = Transaction(sender=wallet.get_address().to_bech32(),
                     receiver=VALIDATOR_CONTRACT,
                     nonce=wallet.get_account().nonce,
                     gas_price=1000000000,
                     gas_limit=200000000,
                     chain_id=chain_id,
                     value=0)

    tx.data = f"unStake@{validator_key.public_address()}".encode()

    # prepare signature
    tx_comp = TransactionComputer()
    result_bytes = tx_comp.compute_bytes_for_signing(tx)

    signature = wallet.get_signer().sign(result_bytes)
    tx.signature = signature

    # send tx
    tx_hash = proxy_default.send_transaction(tx)

    logger.info(f"Unstaking transaction sent for key {validator_key.public_address()}, transaction hash: {tx_hash}")
    return tx_hash


def unBondNodes(wallet: Wallet, validator_key: ValidatorKey) -> str:
    # create transaction
    tx = Transaction(sender=wallet.get_address().to_bech32(),
                     receiver=VALIDATOR_CONTRACT,
                     nonce=wallet.get_account().nonce,
                     gas_price=1000000000,
                     gas_limit=200000000,
                     chain_id=chain_id,
                     value=0)

    tx.data = f"unBondNodes@{validator_key.public_address()}".encode()

    # prepare signature
    tx_comp = TransactionComputer()
    result_bytes = tx_comp.compute_bytes_for_signing(tx)

    signature = wallet.get_signer().sign(result_bytes)
    tx.signature = signature

    # send tx
    tx_hash = proxy_default.send_transaction(tx)

    logger.info(
        f"Un-bonding nodes transaction sent for key {validator_key.public_address()}, transaction hash: {tx_hash}")
    return tx_hash
