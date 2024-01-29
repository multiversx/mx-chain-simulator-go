import json
import time

from multiversx_sdk_core import AddressFactory, TokenComputer, TransactionComputer
from multiversx_sdk_core.transaction_factories import TransactionsFactoryConfig, SmartContractTransactionsFactory, \
    TransferTransactionsFactory
from multiversx_sdk_network_providers import ProxyNetworkProvider
from multiversx_sdk_wallet import UserSigner

SIMULATOR_URL = "http://localhost:8085"
GENERATE_BLOCKS_URL = f"{SIMULATOR_URL}/simulator/generate-blocks"


def main():
    # create a network provider
    provider = ProxyNetworkProvider(SIMULATOR_URL)

    # generate 20 blocks to pass an epoch and the smart contract deploys to be enabled
    provider.do_post(f"{GENERATE_BLOCKS_URL}/25", {})

    # set state for wrapped egld contract and system account on shard 1
    # load JSON data from the file
    with open("state.json", "r") as file:
        json_data = json.load(file)

    provider.do_post(f"{SIMULATOR_URL}/simulator/set-state", json_data)

    with open("state_2.json", "r") as file:
        json_data = json.load(file)

    provider.do_post(f"{SIMULATOR_URL}/simulator/set-state", json_data)

    provider.do_post(f"{GENERATE_BLOCKS_URL}/1", {})

    factory = AddressFactory("erd")
    address = factory.create_from_bech32("erd1hfnw32gkydnj80cljjvkfz9kl3tachmwcpgjhxm5k5l0vhu4pr9s4zwxwa")
    contract_address = factory.create_from_bech32("erd1qqqqqqqqqqqqqpgqzw0d0tj25qme9e4ukverjjjqle6xamay0n4s5r0v9g")

    config = TransactionsFactoryConfig(provider.get_network_config().chain_id)
    tx_factory = TransferTransactionsFactory(config, TokenComputer())
    call_transaction = tx_factory.create_transaction_for_native_token_transfer(
        sender=address,
        receiver=contract_address,
        native_amount=0,
        data=f"ESDTTransfer@5745474c442d613238633539@06f05b59d3b20000@73776170546f6b656e734669786564496e707574@4d45582d613635396430@17b3f233c43fdb2616"
    )
    call_transaction.gas_limit = 510000000
    call_transaction.nonce = provider.get_account(address).nonce
    call_transaction.signature = "0101".encode('utf-8')
    # sign transaction
    # send transaction
    tx_hash = provider.send_transaction(call_transaction)
    print(f"sc call address: {tx_hash}")

    time.sleep(1)

    provider.do_post(f"{GENERATE_BLOCKS_URL}/3", {})


if __name__ == "__main__":
    main()