import base64
import sys
import time
from pathlib import Path

from multiversx_sdk_core import TokenComputer, TransactionComputer, AddressFactory, Address, ContractQueryBuilder
from multiversx_sdk_core.transaction_factories import SmartContractTransactionsFactory, TransactionsFactoryConfig
from multiversx_sdk_network_providers import ProxyNetworkProvider
from multiversx_sdk_network_providers.transactions import TransactionOnNetwork
from multiversx_sdk_wallet import UserPEM, UserSigner

SIMULATOR_URL = "http://localhost:8085"
GENERATE_BLOCKS_URL = f"{SIMULATOR_URL}/simulator/generate-blocks"


def main():
    # create a network provider
    provider = ProxyNetworkProvider(SIMULATOR_URL)

    pem = UserPEM.from_file(Path("../../wallets/wallet.pem"))

    # call proxy faucet
    address = pem.public_key.to_address("erd")
    data = {"receiver": f"{address.to_bech32()}"}
    provider.do_post(f"{SIMULATOR_URL}/transaction/send-user-funds", data)

    # generate 20 blocks to pass an epoch and the smart contract deploys to be enabled
    provider.do_post(f"{GENERATE_BLOCKS_URL}/20", {})

    config = TransactionsFactoryConfig(provider.get_network_config().chain_id)

    sc_factory = SmartContractTransactionsFactory(config, TokenComputer())

    bytecode = Path("./adder.wasm").read_bytes()
    deploy_transaction = sc_factory.create_transaction_for_deploy(
        sender=address,
        bytecode=bytecode,
        arguments=[10],
        gas_limit=10000000,
        is_upgradeable=True,
        is_readable=True,
        is_payable=True,
        is_payable_by_sc=True
    )

    # set nonce
    deploy_transaction.nonce = provider.get_account(address).nonce

    # sign transaction
    user_signer = UserSigner(pem.secret_key)
    tx_computer = TransactionComputer()
    deploy_transaction.signature = user_signer.sign(tx_computer.compute_bytes_for_signing(deploy_transaction))

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

    value  = 10
    contract_address = extract_contract_address(tx_from_network)
    call_transaction = sc_factory.create_transaction_for_execute(
        sender=address,
        contract=contract_address,
        function="add",
        gas_limit=10000000,
        arguments=[value]
    )

    call_transaction.nonce = provider.get_account(address).nonce
    call_transaction.signature = user_signer.sign(tx_computer.compute_bytes_for_signing(call_transaction))

    # send transaction
    tx_hash = provider.send_transaction(deploy_transaction)
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
    factory = AddressFactory("erd")
    for event in tx.logs.events:
        if event.identifier != "SCDeploy":
            continue

        return factory.create_from_hex(event.topics[0].hex())


if __name__ == "__main__":
    main()

