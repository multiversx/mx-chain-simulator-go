import sys
import time
from pathlib import Path

from multiversx_sdk_core import TokenComputer, AddressFactory
from multiversx_sdk_core.transaction_factories import TransactionsFactoryConfig, TokenManagementTransactionsFactory, \
    TransferTransactionsFactory
from multiversx_sdk_network_providers import ProxyNetworkProvider
from multiversx_sdk_wallet import UserPEM

SIMULATOR_URL = "http://localhost:8085"
GENERATE_BLOCKS_URL = f"{SIMULATOR_URL}/simulator/generate-blocks"


def main():
    provider = ProxyNetworkProvider(SIMULATOR_URL)
    pem = UserPEM.from_file(Path("../wallets/wallet.pem"))

    # call proxy faucet
    address = pem.public_key.to_address("erd")
    provider.do_post(f"{SIMULATOR_URL}/transaction/send-user-funds", {"receiver": f"{address.to_bech32()}"})
    provider.do_post(f"{GENERATE_BLOCKS_URL}/3", {})

    # cross-shard transfer
    config = TransactionsFactoryConfig(provider.get_network_config().chain_id)
    tx_factory = TransferTransactionsFactory(config, TokenComputer())
    amount_egld = 1000000000000000000  # 1 egld
    receiver = AddressFactory("erd").create_from_bech32("erd13kp9r5fx4tf8da4ex37sd48pc4xhkmtteq6hcyt4y36pstte0tjqxjf3ns")
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
