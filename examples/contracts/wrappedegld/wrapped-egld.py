import json
import sys
import time

from multiversx_sdk import UserSecretKey
from multiversx_sdk.core import Address
from multiversx_sdk.core import TransactionsFactoryConfig, SmartContractTransactionsFactory
from multiversx_sdk.network_providers import ProxyNetworkProvider

SIMULATOR_URL = "http://localhost:8085"
GENERATE_BLOCKS_URL = f"{SIMULATOR_URL}/simulator/generate-blocks"
WRAPPED_EGLD_TOKEN = "WEGLD-bd4d79"


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

    # set state for wrapped egld contract and system account on shard 1
    # load JSON data from the file
    with open("accounts-state.json", "r") as file:
        json_data = json.load(file)

    provider.do_post(f"{SIMULATOR_URL}/simulator/set-state", json_data)

    wrapp_contract_address = Address.from_bech32(
        "erd1qqqqqqqqqqqqqpgqhe8t5jewej70zupmh44jurgn29psua5l2jps3ntjj3"
    )

    config = TransactionsFactoryConfig(provider.get_network_config().chain_id)
    sc_factory = SmartContractTransactionsFactory(config)
    amount_egld = 5000000000000000000
    call_transaction = sc_factory.create_transaction_for_execute(
        sender=address,
        contract=wrapp_contract_address,
        function="wrapEgld",
        gas_limit=10000000,
        native_transfer_amount=amount_egld,
        arguments=[]
    )

    call_transaction.nonce = provider.get_account(address).nonce
    call_transaction.signature = b"dummy"

    # send transaction
    tx_hash = provider.send_transaction(call_transaction)
    print(f"wrapp egld tx hash: {tx_hash}")

    time.sleep(1)

    # execute 5 block ( transaction needs to be executed on source, block on source has to be finalized...)
    provider.do_post(f"{GENERATE_BLOCKS_URL}/5", {})
    amount = provider.get_fungible_token_of_account(address, WRAPPED_EGLD_TOKEN)
    if amount.balance != amount_egld:
        sys.exit(f"amount of token from balance is no equal with the initial supply: "
                 f"actual-{amount.balance}, expected-{amount_egld}")

    print("transaction was executed, initial address received the wrapped egld token")


if __name__ == "__main__":
    main()
