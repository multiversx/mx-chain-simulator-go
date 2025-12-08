import json
import sys
import time
from pathlib import Path
from typing import Any

from multiversx_sdk import (Address, DelegationTransactionsOutcomeParser,
                            ProxyNetworkProvider, TransactionOnNetwork,
                            TransactionsFactoryConfig,
                            TransferTransactionsFactory, UserSecretKey)

SIMULATOR_URL = "http://localhost:8085"
INITIAL_WALLETS_URL = "simulator/initial-wallets"
GENERATE_BLOCKS_URL = "simulator/generate-blocks"
GENERATE_BLOCKS_UNTIL_EPOCH_REACHED_URL = "simulator/generate-blocks-until-epoch-reached"
GENERATE_BLOCKS_UNTIL_TX_PROCESSED = "simulator/generate-blocks-until-transaction-processed"

parent_directory = Path(__file__).parent

def main():
    # create a network provider
    provider = ProxyNetworkProvider(SIMULATOR_URL)

    key = UserSecretKey.generate()
    address = key.generate_public_key().to_address("erd")
    print(f"working with the generated address: {address.to_bech32()}")

    # call proxy faucet
    data: dict[str, Any] = {
        "receiver": f"{address.to_bech32()}",
        "value": 20000000000000000000000  # 20k eGLD
    }
    provider.do_post_generic("transaction/send-user-funds", data)
    provider.do_post_generic(f"{GENERATE_BLOCKS_URL}/1", {})

    # set balance for an address
    with open(parent_directory / "address.json", "r") as file:
        json_data = json.load(file)

    provider.do_post_generic("simulator/set-state", json_data)

    # generate blocks until the staking mechanism is fully enabled
    provider.do_post_generic(f"{GENERATE_BLOCKS_UNTIL_EPOCH_REACHED_URL}/1", {})

    # ################## create a staking provider
    system_delegation_manager = Address.new_from_bech32(
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
    print(f"create delegation contract tx hash: {tx_hash.hex()}")

    time.sleep(0.5)
    provider.do_post_generic(f"{GENERATE_BLOCKS_UNTIL_TX_PROCESSED}/{tx_hash.hex()}", {})

    # get transaction with status
    tx_from_network = get_tx_and_verify_status(provider, tx_hash.hex())

    # get delegation contract address
    parser = DelegationTransactionsOutcomeParser()
    contract = parser.parse_create_new_delegation_contract(tx_from_network)[0]
    staking_provider_address = contract.contract_address
    print(f"staking provider address: {staking_provider_address.to_bech32()}")

    # ################## merge validator in delegator
    response = provider.do_get_generic(f"{INITIAL_WALLETS_URL}")
    initial_address_with_stake = Address.new_from_bech32(
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
    print(f"white list for merge tx hash: {tx_hash.hex()}")

    time.sleep(0.5)
    provider.do_post_generic(f"{GENERATE_BLOCKS_UNTIL_TX_PROCESSED}/{tx_hash.hex()}", {})

    get_tx_and_verify_status(provider, tx_hash.hex())

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
    print(f"merge validator tx hash: {tx_hash.hex()}")

    time.sleep(0.5)
    # generate 30 blocks to pass an epoch and some rewards will be distributed
    provider.do_post_generic(f"{GENERATE_BLOCKS_URL}/60", {})

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
    print(f"claim rewards tx hash: {tx_hash.hex()}")
    time.sleep(0.5)
    provider.do_post_generic(f"{GENERATE_BLOCKS_UNTIL_TX_PROCESSED}/{tx_hash.hex()}", {})

    # check if the owner receive more than 5 egld in rewards
    claim_reward_tx = get_tx_and_verify_status(provider, tx_hash.hex())
    min_rewards = 400000000000000000
    rewards_value = claim_reward_tx.smart_contract_results[0].raw.get("value", 0)
    if rewards_value < min_rewards:
        sys.exit(f"owner of the delegation contract didn't receive the expected amount of rewards: expected more than "
                 f"0.4 EGLD, received: {rewards_value}")

    print(f"owner has received rewards, received rewards: {rewards_value}")


def get_tx_and_verify_status(provider: ProxyNetworkProvider, tx_hash: str) -> TransactionOnNetwork:
    tx_from_network = provider.get_transaction(tx_hash)
    if not tx_from_network.status.is_successful:
        sys.exit(f"transaction status is not correct, status received->{tx_from_network.status}")

    return tx_from_network


if __name__ == "__main__":
    main()
