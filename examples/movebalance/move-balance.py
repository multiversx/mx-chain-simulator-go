import sys
import time

from multiversx_sdk import UserSecretKey
from multiversx_sdk.core import Address
from multiversx_sdk.core import TransactionsFactoryConfig, TransferTransactionsFactory
from multiversx_sdk.network_providers import ProxyNetworkProvider

SIMULATOR_URL = "http://localhost:8085"
GENERATE_BLOCKS_URL = f"{SIMULATOR_URL}/simulator/generate-blocks"


def main():
    provider = ProxyNetworkProvider(SIMULATOR_URL)

    key = UserSecretKey.generate()
    address = key.generate_public_key().to_address("erd")
    print(f"working with the generated address: {address.to_bech32()}")

    # call proxy faucet
    provider.do_post(f"{SIMULATOR_URL}/transaction/send-user-funds", {"receiver": f"{address.to_bech32()}"})
    provider.do_post(f"{GENERATE_BLOCKS_URL}/3", {})

    # cross-shard transfer
    config = TransactionsFactoryConfig(provider.get_network_config().chain_id)
    tx_factory = TransferTransactionsFactory(config)
    amount_egld = 1000000000000000000  # 1 egld
    receiver = Address.from_bech32(
        "erd13kp9r5fx4tf8da4ex37sd48pc4xhkmtteq6hcyt4y36pstte0tjqxjf3ns"
    )
    call_transaction = tx_factory.create_transaction_for_native_token_transfer(
        sender=address,
        receiver=receiver,
        native_amount=amount_egld,
    )
    call_transaction.gas_limit = 50000
    call_transaction.nonce = provider.get_account(address).nonce
    call_transaction.signature = b"dummy"

    tx_hash = provider.send_transaction(call_transaction)
    print(f"move balance tx hash: {tx_hash}")

    time.sleep(0.5)

    provider.do_post(f"{GENERATE_BLOCKS_URL}/5", {})

    # check receiver balance
    receiver_account = provider.get_account(receiver)
    if receiver_account.balance != amount_egld:
        sys.exit(f"receiver did not receive the transferred amount"
                 f"expected balance: {amount_egld}, current balance: {receiver_account.balance}")


if __name__ == "__main__":
    main()
