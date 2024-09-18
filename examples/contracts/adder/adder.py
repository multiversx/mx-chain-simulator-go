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

    bytecode = Path("./adder.wasm").read_bytes()
    deploy_transaction = sc_factory.create_transaction_for_deploy(
        sender=address,
        bytecode=bytecode,
        arguments=[0],
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

    value = 10
    contract_address = extract_contract_address(tx_from_network)
    call_transaction = sc_factory.create_transaction_for_execute(
        sender=address,
        contract=contract_address,
        function="add",
        gas_limit=10000000,
        arguments=[value]
    )

    call_transaction.nonce = provider.get_account(address).nonce
    call_transaction.signature = b"dummy"

    # send transaction
    tx_hash = provider.send_transaction(call_transaction)
    print(f"sc call tx hash: {tx_hash}")

    time.sleep(0.5)

    # execute 1 block
    provider.do_post(f"{GENERATE_BLOCKS_URL}/1", {})

    # query
    builder = ContractQueryBuilder(
        contract=contract_address,
        function="getSum",
        call_arguments=[],
        caller=address
    )
    query = builder.build()
    response = provider.query_contract(query)
    decoded_bytes = base64.b64decode(response.return_data[0])

    result_int = int.from_bytes(decoded_bytes, byteorder='big')
    print("value:", result_int)
    if value != result_int:
        sys.exit(f"value from vm query is wrong, expected->{value}, received->{result_int}", )


def extract_contract_address(tx: TransactionOnNetwork) -> Address:
    for event in tx.logs.events:
        if event.identifier != "SCDeploy":
            continue

        return Address.from_hex(event.topics[0].hex(), "erd")


if __name__ == "__main__":
    main()
