import sys
import time

from multiversx_sdk import (Address, ProxyNetworkProvider,
                            TransactionsFactoryConfig,
                            TransferTransactionsFactory, UserSecretKey)

SIMULATOR_URL = "http://localhost:8085"
GENERATE_BLOCKS_URL = "simulator/generate-blocks"
GENERATE_BLOCKS_UNTIL_TX_PROCESSED = "simulator/generate-blocks-until-transaction-processed"


def main():
    provider = ProxyNetworkProvider(SIMULATOR_URL)

    key = UserSecretKey.generate()
    address = key.generate_public_key().to_address("erd")
    print(f"working with the generated address: {address.to_bech32()}")

    # call proxy faucet
    provider.do_post_generic("transaction/send-user-funds", {"receiver": f"{address.to_bech32()}"})
    provider.do_post_generic(f"{GENERATE_BLOCKS_URL}/1", {})

    # cross-shard transfer
    config = TransactionsFactoryConfig(provider.get_network_config().chain_id)
    tx_factory = TransferTransactionsFactory(config)
    amount_egld = 1000000000000000000  # 1 egld
    receiver = Address.new_from_bech32(
        "erd13kp9r5fx4tf8da4ex37sd48pc4xhkmtteq6hcyt4y36pstte0tjqxjf3ns"
    )
    call_transaction = tx_factory.create_transaction_for_native_token_transfer(
        sender=address,
        receiver=receiver,
        native_amount=amount_egld,
    )
    call_transaction.nonce = provider.get_account(address).nonce
    call_transaction.signature = b"dummy"

    tx_hash = provider.send_transaction(call_transaction)
    print(f"move balance tx hash: {tx_hash.hex()}")

    time.sleep(0.5)
    # generate enough blocks until the transaction is completed
    provider.do_post_generic(f"{GENERATE_BLOCKS_UNTIL_TX_PROCESSED}/{tx_hash.hex()}", {})

    # check receiver balance
    receiver_account = provider.get_account(receiver)
    if receiver_account.balance != amount_egld:
        sys.exit(f"receiver did not receive the transferred amount"
                 f"expected balance: {amount_egld}, current balance: {receiver_account.balance}")


if __name__ == "__main__":
    main()
