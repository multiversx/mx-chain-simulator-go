import sys

from multiversx_sdk import UserSecretKey
from multiversx_sdk.network_providers import ProxyNetworkProvider
from multiversx_sdk.network_providers.transactions import TransactionOnNetwork
from multiversx_sdk.core import TokenManagementTransactionsFactory, TransactionsFactoryConfig

SIMULATOR_URL = "http://localhost:8085"
GENERATE_BLOCKS_UNTIL_TX_PROCESSED = f"{SIMULATOR_URL}/simulator/generate-blocks-until-transaction-processed"
GENERATE_BLOCKS_UNTIL_EPOCH_REACHED_URL = f"{SIMULATOR_URL}/simulator/generate-blocks-until-epoch-reached"


def main():
    # create a network provider
    provider = ProxyNetworkProvider(SIMULATOR_URL)

    key = UserSecretKey.generate()
    address = key.generate_public_key().to_address("erd")
    print(f"working with the generated address: {address.to_bech32()}")

    # call proxy faucet
    data = {"receiver": f"{address.to_bech32()}"}
    provider.do_post(f"{SIMULATOR_URL}/transaction/send-user-funds", data)

    # generate blocks until ESDTs are enabled
    provider.do_post(f"{GENERATE_BLOCKS_UNTIL_EPOCH_REACHED_URL}/1", {})

    # create transaction config and factory
    config = TransactionsFactoryConfig(provider.get_network_config().chain_id)
    transaction_factory = TokenManagementTransactionsFactory(config)

    # create issue transaction
    initial_supply = 100000
    tx = transaction_factory.create_transaction_for_issuing_fungible(
        sender=address,
        token_name="tttt",
        token_ticker="TTTT",
        initial_supply=initial_supply,
        num_decimals=1,
        can_pause=False,
        can_wipe=False,
        can_freeze=False,
        can_upgrade=False,
        can_change_owner=False,
        can_add_special_roles=False,
    )

    # set issue cost and nonce
    tx.amount = 50000000000000000  # 0.05 EGLD
    tx.nonce = provider.get_account(address).nonce
    tx.signature = b"dummy"

    # send transaction
    tx_hash = provider.send_transaction(tx)
    print(f"generated tx hash: {tx_hash}")

    # wait for the transaction to be completed
    provider.do_post(f"{GENERATE_BLOCKS_UNTIL_TX_PROCESSED}/{tx_hash}", {})

    # get transaction with status
    tx_from_network = provider.get_transaction(tx_hash, with_process_status=True)

    # verify transaction status and account balance
    if not tx_from_network.status.is_successful():
        sys.exit(f"transaction status is not correct, status received->{tx_from_network.status}")

    # verify token balance
    token_identifier_string = extract_token_identifier(tx_from_network)
    amount = provider.get_fungible_token_of_account(address, token_identifier_string)
    if amount.balance != initial_supply:
        sys.exit(f"amount of token from balance is no equal with the initial supply: "
                 f"actual-{amount.balance}, expected-{initial_supply}")

    print("transaction was executed and tokens were created")


def extract_token_identifier(tx: TransactionOnNetwork) -> str:
    for event in tx.logs.events:
        if event.identifier != "upgradeProperties":
            continue

        decoded_bytes = bytes.fromhex(event.topics[0].hex())
        return decoded_bytes.decode('utf-8')

    return ""


if __name__ == "__main__":
    main()
