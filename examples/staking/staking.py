import json
import sys
import time

from multiversx_sdk import UserSecretKey
from multiversx_sdk.core import Address
from multiversx_sdk.core import TransactionsFactoryConfig, TransferTransactionsFactory
from multiversx_sdk.network_providers import ProxyNetworkProvider
from multiversx_sdk.network_providers.transactions import TransactionOnNetwork

SIMULATOR_URL = "http://localhost:8085"
INITIAL_WALLETS_URL = f"{SIMULATOR_URL}/simulator/initial-wallets"
GENERATE_BLOCKS_URL = f"{SIMULATOR_URL}/simulator/generate-blocks"


def main():
    # create a network provider
    provider = ProxyNetworkProvider(SIMULATOR_URL)

    key = UserSecretKey.generate()
    address = key.generate_public_key().to_address("erd")
    print(f"working with the generated address: {address.to_bech32()}")

    # call proxy faucet
    data = {
        "receiver": f"{address.to_bech32()}",
        "value": 20000000000000000000000  # 20k eGLD
    }
    provider.do_post(f"{SIMULATOR_URL}/transaction/send-user-funds", data)
    provider.do_post(f"{GENERATE_BLOCKS_URL}/3", {})

    # set balance for an address
    with open("address.json", "r") as file:
        json_data = json.load(file)

    provider.do_post(f"{SIMULATOR_URL}/simulator/set-state", json_data)

    # generate 20 blocks to pass an epoch and the smart contract deploys to be enabled
    provider.do_post(f"{GENERATE_BLOCKS_URL}/20", {})

    # ################## create a staking provider
    system_delegation_manager = Address.from_bech32(
        "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqylllslmq6y6"
    )
    config = TransactionsFactoryConfig(provider.get_network_config().chain_id)
    tx_factory = TransferTransactionsFactory(config)
    amount_egld = 1250000000000000000000  # 1250 egld
    call_transaction = tx_factory.create_transaction_for_native_token_transfer(
        sender=address,
        receiver=system_delegation_manager,
        native_amount=amount_egld,
        data="createNewDelegationContract@00@0ea1"
    )
    call_transaction.gas_limit = 65000000
    call_transaction.nonce = provider.get_account(address).nonce
    call_transaction.signature = b"dummy"

    # send transaction
    tx_hash = provider.send_transaction(call_transaction)
    print(f"create delegation contract tx hash: {tx_hash}")

    time.sleep(0.5)
    provider.do_post(f"{GENERATE_BLOCKS_URL}/5", {})

    # get transaction with status
    tx_from_network = get_tx_and_verify_status(provider, tx_hash)

    staking_provider_address = extract_contract_address(tx_from_network)
    print(f"staking provider address: {staking_provider_address.to_bech32()}")

    # ################## merge validator in delegator
    response = provider.do_get(f"{INITIAL_WALLETS_URL}")
    initial_address_with_stake = Address.from_bech32(
        response.to_dictionary()["stakeWallets"][0]["address"]["bech32"]
    )

    print(f"initial address with stake: {initial_address_with_stake.to_bech32()}, "
          f"balance: {provider.get_account(initial_address_with_stake).balance}")

    # white list transaction
    call_transaction = tx_factory.create_transaction_for_native_token_transfer(
        sender=address,
        receiver=staking_provider_address,
        native_amount=0,
        data=f"whitelistForMerge@{initial_address_with_stake.to_hex()}"
    )

    call_transaction.gas_limit = 65000000
    call_transaction.nonce = provider.get_account(address).nonce
    call_transaction.signature = b"dummy"
    tx_hash = provider.send_transaction(call_transaction)
    print(f"white list for merge tx hash: {tx_hash}")

    time.sleep(0.5)
    provider.do_post(f"{GENERATE_BLOCKS_URL}/5", {})

    get_tx_and_verify_status(provider, tx_hash)

    # merge transaction
    call_transaction = tx_factory.create_transaction_for_native_token_transfer(
        sender=initial_address_with_stake,
        receiver=system_delegation_manager,
        native_amount=0,
        data=f"mergeValidatorToDelegationWithWhitelist@{staking_provider_address.to_hex()}"
    )

    call_transaction.gas_limit = 510000000
    call_transaction.nonce = provider.get_account(initial_address_with_stake).nonce
    call_transaction.signature = b"dummy"
    tx_hash = provider.send_transaction(call_transaction)
    print(f"merge validator tx hash: {tx_hash}")

    time.sleep(0.5)
    # generate 30 blocks to pass an epoch and some rewards will be distributed
    provider.do_post(f"{GENERATE_BLOCKS_URL}/30", {})

    # check if the owner of the delegation contract has rewards
    call_transaction = tx_factory.create_transaction_for_native_token_transfer(
        sender=address,
        receiver=staking_provider_address,
        native_amount=0,
        data=f"claimRewards"
    )
    call_transaction.gas_limit = 510000000
    call_transaction.nonce = provider.get_account(address).nonce
    call_transaction.signature = b"dummy"
    tx_hash = provider.send_transaction(call_transaction)
    print(f"claim rewards tx hash: {tx_hash}")
    time.sleep(0.5)
    provider.do_post(f"{GENERATE_BLOCKS_URL}/5", {})

    # check if the owner receive more than 5 egld in rewards
    claim_reward_tx = get_tx_and_verify_status(provider, tx_hash)
    one_egld = 1000000000000000000
    rewards_value = claim_reward_tx.contract_results.items[0].value
    if rewards_value < one_egld:
        sys.exit(f"owner of the delegation contract didn't receive the expected amount of rewards: expected more than "
                 f"1 EGLD, received: {rewards_value}")

    print(f"owner has received rewards, received rewards: {rewards_value}")


def extract_contract_address(tx: TransactionOnNetwork) -> Address:
    for event in tx.logs.events:
        if event.identifier != "SCDeploy":
            continue

        return Address.from_hex(event.topics[0].hex(), "erd")


def get_tx_and_verify_status(provider: ProxyNetworkProvider, tx_hash: str) -> TransactionOnNetwork:
    tx_from_network = provider.get_transaction(tx_hash, with_process_status=True)
    if not tx_from_network.status.is_successful():
        sys.exit(f"transaction status is not correct, status received->{tx_from_network.status}")

    return tx_from_network


if __name__ == "__main__":
    main()
