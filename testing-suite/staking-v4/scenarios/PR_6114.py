import threading
import time


from core.validatorKey import *
from core.chain_simulator import *
from chain_commander import *
from staking import stake, unStake, unBondNodes
from network_provider.get_validator_info import get_keys_state, get_keys_from_validator_statistics, \
    get_keys_from_validator_auction
from network_provider.key_management import add_blocks_until_key_eligible, add_key

import requests


# SCENARIO 1
# Have every epoch auction list with enough nodes (let's say 8 qualified, 2 unqualified)
# Unstake 1 or more eligible/waiting nodes (no more than all nodes per shard or no more than all eligible)
# and call auction list api; we should see 8 qualified nodes. Next epoch we need to check that exactly 8 nodes were qualified.
# Afterwards(some epochs), those leaving nodes will be leaving and replaced by the auction nodes

# Testnet configuration:
# num_validators_per_shard = 10
# num_validators_meta = 10
# num_waiting_validators_per_shard = 6
# num_waiting_validators_meta = 6
# nodes_to_shuffle_per_shard = 2

# from this config results:
#   eligible nodes = 10*4 = 40
#   waiting nodes = (6 - 2 (auction)) * 4 = 16
#   auction nodes = 2*4 = 8

# Steps:
# 1) In epoch 5 stake with A that 2 keys  - will go in auction
# 2) Add blocks and epochs until 1 of this 2 keys are eligible - let's call it epoch X
# 3) unStake the eligible key in epoch X
# 4) call auction list api after 2 blocks (we are still in epoch X) and:
#       4.1) unStaked key status should be "eligible (leaving)" on validator/statistics
#       4.2) we should have still 8 keys qualified
#       4.3) we should have still 2 keys not qualified
#       4.4) we should have 39 keys with status "eligible"
#       4.5) we should have still 16 keys with status "waiting"
# 5) go to epoch X+1  and 5 blocks and make sure:
#       5.1) unstaked key should be inactive
#       5.2) 8 keys were selected from auction in epoch x and are now waiting
#       5.3) we will now have 9 keys in auction, 8 of them are qualified, 1 not qualified , 40 keys eligible, 16 waiting


def main():
    print("Happy testing")


def test_PR_6114():

    # === PRE-CONDITIONS ==============================================================
    AMOUNT_TO_MINT = "10000" + "000000000000000000"

    wallet_a = Wallet(Path("./wallets/walletKey_1.pem"))
    key_1 = ValidatorKey(Path("./validatorKeys/validatorKey_1.pem"))
    key_2 = ValidatorKey(Path("./validatorKeys/validatorKey_2.pem"))
    all_keys = [key_1, key_2]

    # check if minting is successful
    assert "success" in wallet_a.set_balance(AMOUNT_TO_MINT)

    # add some blocks
    response = add_blocks(5)
    assert "success" in response
    time.sleep(0.5)

    # check balance
    assert wallet_a.get_balance() == AMOUNT_TO_MINT

    # add keys to protocol. This way staked keys will not go to jail.
    assert "success" in add_key(all_keys)

    # move to epoch
    assert "success" in add_blocks_until_epoch_reached(5)

    # === STEP 1 ==============================================================
    # 1) In epoch 5 stake with A that 2 keys  - will go in auction

    tx_hash = stake(wallet_a, all_keys)

    # check if tx is success
    assert "success" in add_blocks_until_tx_fully_executed(tx_hash)

    # check that nodes are staked
    for key in all_keys:
        assert "staked" in key.get_status(wallet_a.public_address())

    # move 2 blocks before calling validator/statistics
    assert "success" in add_blocks(2)
    time.sleep(1)

    # check that nodes are in auction
    for key in all_keys:
        assert "auction" in key.get_state()

    # === STEP 2 ==============================================================
    # 2) Add blocks and epochs until 1 of this 2 keys are eligible - let's call it epoch X

    eligible_key = add_blocks_until_key_eligible(all_keys)

    current_epoch = proxy_default.get_network_status().epoch_number
    print("Eligible key: ", eligible_key.public_address())
    print("Current epoch:", current_epoch)

    # === STEP 3 ==============================================================
    # 3) unStake the eligible key in epoch X

    tx_hash = unStake(wallet_a, eligible_key)

    # check if tx is success
    assert "success" in add_blocks_until_tx_fully_executed(tx_hash)

    current_epoch = proxy_default.get_network_status().epoch_number
    print("Key unstaked in epoch:", current_epoch)

    # check if key is now unStaked on getBlsKeyStatus
    assert "unStaked" in eligible_key.get_status(wallet_a.public_address())

    # eligible_key becomes un_staked_key to be easier to read the test
    un_staked_key = eligible_key

    # === STEP 4 ==============================================================
    # 4) call auction list api after 2 blocks and:

    # wait 1 sec and move to the last block of epoch before saving all qualified and unqualified keys
    time.sleep(1)
    assert "success" in add_blocks_until_last_block_of_current_epoch()

    # 4.1) unStaked key status should be "eligible (leaving)" on validator/statistics
    assert un_staked_key.get_state() == "eligible (leaving)"

    epoch_x = proxy_default.get_network_status().epoch_number
    print("Key is leaving in epoch:", epoch_x)

    # 4.2) we should have still 8 keys qualified
    qualified_keys_in_epoch_x = get_keys_from_validator_auction(isQualified=True)
    assert len(qualified_keys_in_epoch_x) == 8

    # 4.3) we should have still 2 keys not qualified
    not_qualified_keys_in_epoch_x = get_keys_from_validator_auction(isQualified=False)
    assert len(not_qualified_keys_in_epoch_x) == 2

    # 4.4) we should have 39 keys with status "eligible"
    eligible_keys_in_epoch_x = get_keys_from_validator_statistics(needed_state="eligible")
    assert len(eligible_keys_in_epoch_x) == 39

    # 4.5) we should have still 16 keys with status "waiting"
    waiting_keys_in_epoch_x = get_keys_from_validator_statistics(needed_state="waiting")
    assert len(waiting_keys_in_epoch_x) == 16

    # === STEP 5 ==============================================================
    # 5) go to epoch X+1  and 5 blocks and make sure:

    # go to epoch X+1
    assert "success" in add_blocks_until_epoch_reached(epoch_x + 1)
    print("Epoch: ", epoch_x + 1)

    # add 5 block
    assert "success" in add_blocks(5)

    # 5.1) unstaked key should be inactive
    assert "inactive" == eligible_key.get_state()
    print("key", un_staked_key.get_state())

    # 5.2) 8 keys were selected from auction in epoch x and are now waiting
    all_auction_keys_from_epoch_x = qualified_keys_in_epoch_x + not_qualified_keys_in_epoch_x
    waiting_keys_now = get_keys_from_validator_statistics("waiting")
    to_be_checked_list = []
    for key in all_auction_keys_from_epoch_x:
        if key in waiting_keys_now:
            to_be_checked_list.append(key)
    assert len(to_be_checked_list) == 8

    # 5.3) we will now have 9 keys in auction, 8 of them are qualified, 1 not qualified , 40 keys eligible, 16 waiting
    qualified_keys = get_keys_from_validator_auction(isQualified=True)
    assert len(qualified_keys) == 8

    not_qualified_keys = get_keys_from_validator_auction(isQualified=False)
    assert len(not_qualified_keys) == 1

    eligible_keys = get_keys_from_validator_statistics("eligible")
    assert len(eligible_keys) == 40

    waiting_keys = get_keys_from_validator_statistics("waiting")
    assert len(waiting_keys) == 16


if __name__ == '__main__':
    main()
