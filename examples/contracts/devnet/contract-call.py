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

    factory = AddressFactory("erd")
    address = factory.create_from_bech32("erd1tzq44fl4a6yl8l7zgrvv7kpgvscq9xu05uyu6fekez9pcclvxs5stp4vgw")
    contract_address = factory.create_from_bech32("erd1qqqqqqqqqqqqqpgqsp7wpnxv8lpn6hg4fhhp3vqkwmst5ljm2krs2fxjrk")

    config = TransactionsFactoryConfig(provider.get_network_config().chain_id)
    tx_factory = TransferTransactionsFactory(config, TokenComputer())
    call_transaction = tx_factory.create_transaction_for_native_token_transfer(
        sender=address,
        receiver=contract_address,
        native_amount=0,
        data=f"ESDTTransfer@444556445553542d643632393831@056bc75e2d63100000@627579@4445565348414c414e2d393333663830@04"
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