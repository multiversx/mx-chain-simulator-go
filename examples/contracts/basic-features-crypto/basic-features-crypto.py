import base64
import sys
import time
from pathlib import Path

from multiversx_sdk import UserSecretKey
from multiversx_sdk.core import Address, ContractQueryBuilder
from multiversx_sdk.core import SmartContractTransactionsFactory, TransactionsFactoryConfig
from multiversx_sdk.network_providers import ProxyNetworkProvider
from multiversx_sdk.network_providers.transactions import TransactionOnNetwork

SIMULATOR_URL = "http://localhost:8085"
GENERATE_BLOCKS_UNTIL_EPOCH_REACHED_URL = f"{SIMULATOR_URL}/simulator/generate-blocks-until-epoch-reached"
GENERATE_BLOCKS_UNTIL_TX_PROCESSED = f"{SIMULATOR_URL}/simulator/generate-blocks-until-transaction-processed"


def main():
    # create a network provider
    provider = ProxyNetworkProvider(SIMULATOR_URL)

    key = UserSecretKey.generate()
    address = key.generate_public_key().to_address("erd")
    print(f"working with the generated address: {address.to_bech32()}")

    # call proxy faucet
    data = {"receiver": f"{address.to_bech32()}"}
    provider.do_post(f"{SIMULATOR_URL}/transaction/send-user-funds", data)

    # generate blocks until smart contract deploys are enabled
    provider.do_post(f"{GENERATE_BLOCKS_UNTIL_EPOCH_REACHED_URL}/1", {})

    config = TransactionsFactoryConfig(provider.get_network_config().chain_id)

    sc_factory = SmartContractTransactionsFactory(config)

    bytecode = Path("../basic-features-crypto/basic-features-crypto.wasm").read_bytes()
    deploy_transaction = sc_factory.create_transaction_for_deploy(
        sender=address,
        bytecode=bytecode,
        arguments=[],
        gas_limit=10000000,
        is_upgradeable=True,
        is_readable=True,
        is_payable=True,
        is_payable_by_sc=True
    )

    # set nonce
    deploy_transaction.nonce = provider.get_account(address).nonce
    deploy_transaction.signature = b"dummy"

    # send transaction
    tx_hash = provider.send_transaction(deploy_transaction)
    print(f"deploy tx hash: {tx_hash}")

    time.sleep(0.5)
    # generate enough blocks until the transaction is completed
    provider.do_post(f"{GENERATE_BLOCKS_UNTIL_TX_PROCESSED}/{tx_hash}", {})

    # get transaction with status
    tx_from_network = provider.get_transaction(tx_hash, with_process_status=True)

    # verify transaction status and account balance
    if not tx_from_network.status.is_successful():
        sys.exit(f"transaction status is not correct, status received->{tx_from_network.status}")


if __name__ == "__main__":
    main()
