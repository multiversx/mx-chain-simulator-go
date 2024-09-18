import sys
import time
from pathlib import Path

from multiversx_sdk import UserSecretKey
from multiversx_sdk.core import Address
from multiversx_sdk.core import SmartContractTransactionsFactory, TransactionsFactoryConfig
from multiversx_sdk.network_providers import ProxyNetworkProvider
from multiversx_sdk.network_providers.transactions import TransactionOnNetwork

SIMULATOR_URL = "http://localhost:8085"
GENERATE_BLOCKS_URL = f"{SIMULATOR_URL}/simulator/generate-blocks"


def main():
    # create a network provider
    provider = ProxyNetworkProvider(SIMULATOR_URL)

    key = UserSecretKey.generate()
    address = key.generate_public_key().to_address("erd")
    print(f"working with the generated address: {address.to_bech32()}")

    # call proxy faucet
    data = {"receiver": f"{address.to_bech32()}"}
    provider.do_post(f"{SIMULATOR_URL}/transaction/send-user-funds", data)

    # generate 20 blocks to pass an epoch and the smart contract deploys to be enabled
    provider.do_post(f"{GENERATE_BLOCKS_URL}/20", {})

    config = TransactionsFactoryConfig(provider.get_network_config().chain_id)

    sc_factory = SmartContractTransactionsFactory(config)

    bytecode = Path("./contract.wasm").read_bytes()
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

    # execute 1 block
    provider.do_post(f"{GENERATE_BLOCKS_URL}/1", {})

    # get transaction with status
    tx_from_network = provider.get_transaction(tx_hash, with_process_status=True)

    # verify transaction status and account balance
    if not tx_from_network.status.is_successful():
        sys.exit(f"transaction status is not correct, status received->{tx_from_network.status}")

    contract_address = extract_contract_address(tx_from_network)
    call_transaction = sc_factory.create_transaction_for_execute(
        sender=address,
        contract=contract_address,
        function="issue",
        gas_limit=100000000,
        arguments=[]
    )

    call_transaction.amount = 10000000000000000
    call_transaction.nonce = provider.get_account(address).nonce
    call_transaction.signature = b"dummy"

    # send transaction
    tx_hash = provider.send_transaction(call_transaction)
    print(f"sc call tx hash: {tx_hash}")

    time.sleep(0.5)

    provider.do_post(f"{GENERATE_BLOCKS_URL}/3", {})

    status = get_processed_status(provider, tx_hash)
    if status != "pending":
        sys.exit(f"incorrect status of transaction: expected->pending, received->{status}")

    provider.do_post(f"{GENERATE_BLOCKS_URL}/3", {})
    status = get_processed_status(provider, tx_hash)
    if status != "fail":
        sys.exit(f"incorrect status of transaction: expected->fail, received->{status}")


def get_processed_status(provider, tx_hash):
    response = provider.do_get(f"{SIMULATOR_URL}/transaction/{tx_hash}/process-status")

    return response.get("status")


def extract_contract_address(tx: TransactionOnNetwork) -> Address:
    for event in tx.logs.events:
        if event.identifier != "SCDeploy":
            continue

        return Address.from_hex(event.topics[0].hex(), "erd")


if __name__ == "__main__":
    main()
