import sys
import time
from pathlib import Path

from multiversx_sdk import Account, NetworkEntrypoint, UserSecretKey
from multiversx_sdk.abi import Abi

SIMULATOR_URL = "http://localhost:8085"
GENERATE_BLOCKS_UNTIL_EPOCH_REACHED_URL = "simulator/generate-blocks-until-epoch-reached"
GENERATE_BLOCKS_UNTIL_TX_PROCESSED = "simulator/generate-blocks-until-transaction-processed"

parent_directory = Path(__file__).parent

def main():
    entrypoint = NetworkEntrypoint(
        network_provider_url=SIMULATOR_URL,
        network_provider_kind="proxy",
        chain_id="chain"
    )

    # create a network provider
    provider = entrypoint.create_network_provider()

    key = UserSecretKey.generate()

    # create Account
    account = Account(key)
    print(f"working with the generated address: {account.address.to_bech32()}")

    # call proxy faucet
    data = {"receiver": f"{account.address.to_bech32()}"}
    provider.do_post_generic("transaction/send-user-funds", data)

    # fetch nonce
    account.nonce = entrypoint.recall_account_nonce(account.address)

    # generate blocks until smart contract deploys are enabled
    provider.do_post_generic(f"{GENERATE_BLOCKS_UNTIL_EPOCH_REACHED_URL}/1", {})

    # load ABI from file and create controller
    abi = Abi.load(parent_directory / "adder.abi.json")
    sc_controller = entrypoint.create_smart_contract_controller(abi=abi)

    bytecode = (parent_directory / "adder.wasm").read_bytes()
    deploy_transaction = sc_controller.create_transaction_for_deploy(
        sender=account,
        nonce=account.get_nonce_then_increment(),
        bytecode=bytecode,
        arguments=[0],
        gas_limit=10000000,
        is_upgradeable=True,
        is_readable=True,
        is_payable=True,
        is_payable_by_sc=True
    )

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

    value = 10
    contract_address = sc_controller.parse_deploy(tx_from_network).contracts[0].address
    call_transaction = sc_controller.create_transaction_for_execute(
        sender=account,
        nonce=account.get_nonce_then_increment(),
        contract=contract_address,
        function="add",
        gas_limit=10000000,
        arguments=[value]
    )

    # send transaction
    tx_hash = provider.send_transaction(call_transaction)
    print(f"sc call tx hash: {tx_hash.hex()}")

    time.sleep(0.5)
    # generate enough blocks until the transaction is completed
    provider.do_post_generic(f"{GENERATE_BLOCKS_UNTIL_TX_PROCESSED}/{tx_hash.hex()}", {})

    # query contract
    response = sc_controller.query(
        contract=contract_address,
        function="getSum",
        arguments=[]
    )[0]

    print("value:", response)
    if value != response:
        sys.exit(f"value from vm query is wrong, expected->{value}, received->{response}")


if __name__ == "__main__":
    main()
