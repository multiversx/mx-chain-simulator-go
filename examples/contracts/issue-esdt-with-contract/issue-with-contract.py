import sys
import time
from pathlib import Path

from multiversx_sdk import (ProxyNetworkProvider,
                            SmartContractTransactionsFactory,
                            SmartContractTransactionsOutcomeParser,
                            TransactionsFactoryConfig, UserSecretKey)

SIMULATOR_URL = "http://localhost:8085"
GENERATE_BLOCKS_URL = "/simulator/generate-blocks"
GENERATE_BLOCKS_UNTIL_EPOCH_REACHED_URL = "simulator/generate-blocks-until-epoch-reached"
GENERATE_BLOCKS_UNTIL_TX_PROCESSED = "simulator/generate-blocks-until-transaction-processed"

parent_directory = Path(__file__).parent


def main():
    # create a network provider
    provider = ProxyNetworkProvider(SIMULATOR_URL)

    key = UserSecretKey.generate()
    address = key.generate_public_key().to_address("erd")
    print(f"working with the generated address: {address.to_bech32()}")

    # call proxy faucet
    data = {"receiver": f"{address.to_bech32()}"}
    provider.do_post_generic("transaction/send-user-funds", data)

    # generate blocks until smart contract deploys & ESDTs are enabled
    provider.do_post_generic(f"{GENERATE_BLOCKS_UNTIL_EPOCH_REACHED_URL}/1", {})

    config = TransactionsFactoryConfig(provider.get_network_config().chain_id)
    sc_factory = SmartContractTransactionsFactory(config)

    bytecode = (parent_directory / "contract.wasm").read_bytes()
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
    print(f"deploy tx hash: {tx_hash.hex()}")

    time.sleep(0.5)
    # generate enough blocks until the transaction is completed
    provider.do_post_generic(f"{GENERATE_BLOCKS_UNTIL_TX_PROCESSED}/{tx_hash.hex()}", {})

    # get transaction with status
    tx_from_network = provider.get_transaction(tx_hash)

    # verify transaction status and account balance
    if not tx_from_network.status.is_successful:
        sys.exit(f"transaction status is not correct, status received->{tx_from_network.status.status}")

    # extract contract address
    parser = SmartContractTransactionsOutcomeParser()
    contracts = parser.parse_deploy(tx_from_network).contracts
    contract_address = contracts[0].address

    call_transaction = sc_factory.create_transaction_for_execute(
        sender=address,
        contract=contract_address,
        function="issue",
        gas_limit=100000000,
        arguments=[]
    )

    call_transaction.value = 10000000000000000
    call_transaction.nonce = provider.get_account(address).nonce
    call_transaction.signature = b"dummy"

    # send transaction
    tx_hash = provider.send_transaction(call_transaction)
    print(f"sc call tx hash: {tx_hash.hex()}")

    time.sleep(0.5)

    provider.do_post_generic(f"{GENERATE_BLOCKS_URL}/1", {})

    status = provider.get_transaction_status(tx_hash)
    if status.status != "pending":
        sys.exit(f"incorrect status of transaction: expected->pending, received->{status}")

    provider.do_post_generic(f"{GENERATE_BLOCKS_URL}/4", {})
    status = status = provider.get_transaction_status(tx_hash)
    if status.status != "fail":
        sys.exit(f"incorrect status of transaction: expected->fail, received->{status}")


if __name__ == "__main__":
    main()
