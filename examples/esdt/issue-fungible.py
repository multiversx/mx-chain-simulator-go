import sys
import time

from multiversx_sdk_network_providers import ProxyNetworkProvider
from multiversx_sdk_network_providers.transactions import TransactionOnNetwork
from multiversx_sdk_core.transaction_factories import TokenManagementTransactionsFactory, TransactionsFactoryConfig
from multiversx_sdk_core import TransactionComputer
from multiversx_sdk_wallet import UserPEM, UserSigner
from pathlib import Path

SIMULATOR_URL = "http://localhost:8085"
GENERATE_BLOCKS_URL = f"{SIMULATOR_URL}/simulator/generate-blocks"
GENERATE_BLOCKS_UNTIL_TX_PROCESSED = f"{SIMULATOR_URL}/simulator/generate-blocks-until-transaction-processed"


def main():
    # create a network provider
    provider = ProxyNetworkProvider(SIMULATOR_URL)

    pem = UserPEM.from_file(Path("../wallets/wallet.pem"))

    # call proxy faucet
    address = pem.public_key.to_address("erd")
    data = {"receiver": f"{address.to_bech32()}"}
    provider.do_post(f"{SIMULATOR_URL}/transaction/send-user-funds", data)

    # generate 20 blocks to pass an epoch and the ESDT contract to be enabled
    provider.do_post(f"{GENERATE_BLOCKS_URL}/20", {})

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
    tx.amount = 5000000000000000000
    tx.nonce = provider.get_account(address).nonce

    # sign transaction
    user_signer = UserSigner(pem.secret_key)
    tx_computer = TransactionComputer()
    tx.signature = user_signer.sign(tx_computer.compute_bytes_for_signing(tx))

    # send transaction
    tx_hash = provider.send_transaction(tx)
    print(f"generated tx hash: {tx_hash}")
    time.sleep(1)

    # execute 5 block ( transaction needs to be executed on source, block on source has to be finalized...)
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
        sys.exit(f"amount of token from balance is no equal with the initial supply: actual-{amount.balance}, expected-{initial_supply}")

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
