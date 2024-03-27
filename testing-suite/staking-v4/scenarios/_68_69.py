# Config:
# -num-validators-per-shard 10
# -num-waiting-validators-per-shard 6
# -num-validators-meta 10
# -num-waiting-validators-meta 6
# max nr of nodes that a SP should have = 10% * total num validators (=40)  = 4

# Steps :
# - We have Addresses A B C and D
# - 1) Stake 4 nodes with B in epoch 4
# - 2) Stake 2 nodes with C in epoch 4
# - 3) Stake 2 nodes with D in epoch 4
# - 4) Create a delegation contract with A
# - 5) Merge C nodes in A's contract - should succeed
# - 6) Merge D nodes in A's contract - should succeed
# - 7) Merge B nodes in A's contract - should fail

import delegation
import time
from config import *
from delegation import *
from chain_commander import *
from get_info import *
from staking import *
from delegation import *
from core.wallet import *
from core.validatorKey import *


def main():
    print("Happy testing")


def test_68_69():

    # # TODO: add cli param for epochs , so we can re-run the test in different epochs for staking-v4 activation

    # === PRE-REQUIRES ==============================================================
    # mint addresses
    AMMOUNT_TO_MINT = "50000" + "000000000000000000"

    _A = Wallet(Path("./wallets/walletKey_1.pem"))
    _B = Wallet(Path("./wallets/walletKey_2.pem"))
    _C = Wallet(Path("./wallets/walletKey_3.pem"))
    _D = Wallet(Path("./wallets/walletKey_4.pem"))

    # check minting request will succeed
    assert "success" in _A.set_balance(AMMOUNT_TO_MINT)
    assert "success" in _B.set_balance(AMMOUNT_TO_MINT)
    assert "success" in _C.set_balance(AMMOUNT_TO_MINT)
    assert "success" in _D.set_balance(AMMOUNT_TO_MINT)

    # add some blocks
    response = addBlocks(5)
    assert "success" in response
    time.sleep(0.5)

    # check balances
    assert _A.get_balance() == AMMOUNT_TO_MINT
    assert _B.get_balance() == AMMOUNT_TO_MINT
    assert _C.get_balance() == AMMOUNT_TO_MINT
    assert _D.get_balance() == AMMOUNT_TO_MINT

    # go to epoch 4 , so you can stake nodes without auto-unStake them in epoch 4
    time.sleep(1)
    response = addBlocksUntilEpochReached(4)
    assert "success" in response

    # === STEP 1 ===============================================================
    # 1) Stake 4 nodes with B
    VALIDATOR_KEY_1 = ValidatorKey(Path("./validatorKeys/validatorKey_1.pem"))
    VALIDATOR_KEY_2 = ValidatorKey(Path("./validatorKeys/validatorKey_2.pem"))
    VALIDATOR_KEY_3 = ValidatorKey(Path("./validatorKeys/validatorKey_3.pem"))
    VALIDATOR_KEY_4 = ValidatorKey(Path("./validatorKeys/validatorKey_4.pem"))
    B_valid_keys_list = [VALIDATOR_KEY_1, VALIDATOR_KEY_2, VALIDATOR_KEY_3, VALIDATOR_KEY_4]

    # stake
    tx_hash = stake(_B, B_valid_keys_list)

    # move 5 blocks
    response = addBlocks(5)
    assert "success" in response

    # check if tx succeeded
    time.sleep(1)
    assert getStatusOfTx(tx_hash) == "success"

    # check bls keys statuses
    for key in B_valid_keys_list:
        assert key.get_status(_B) == "staked"

    # check if owner is B
    for key in B_valid_keys_list:
        assert key.belongs_to(_B)

    # === STEP 2 ================================================================
    # 2) Stake 2 nodes with C in epoch 4
    VALIDATOR_KEY_5 = ValidatorKey(Path("./validatorKeys/validatorKey_5.pem"))
    VALIDATOR_KEY_6 = ValidatorKey(Path("./validatorKeys/validatorKey_6.pem"))
    C_valid_keys_list = [VALIDATOR_KEY_5, VALIDATOR_KEY_6]

    # stake
    tx_hash = stake(_C, C_valid_keys_list)

    # move 5 blocks
    response = addBlocks(5)
    assert "success" in response
    # check if tx succeeded
    time.sleep(1)
    assert getStatusOfTx(tx_hash) == "success"

    # check bls keys statuses
    for key in C_valid_keys_list:
        assert key.get_status(_C) == "staked"

    # check if owner is C
    for key in C_valid_keys_list:
        assert key.belongs_to(_C)

    # === STEP 3 ============================================================
    # 3) Stake 2 nodes with D in epoch 4
    VALIDATOR_KEY_7 = ValidatorKey(Path("./validatorKeys/validatorKey_7.pem"))
    VALIDATOR_KEY_8 = ValidatorKey(Path("./validatorKeys/validatorKey_8.pem"))
    D_valid_keys_list = [VALIDATOR_KEY_7, VALIDATOR_KEY_8]

    # stake
    tx_hash = stake(_D, D_valid_keys_list)

    # move 5 blocks
    response = addBlocks(5)
    assert "success" in response
    time.sleep(1)
    # check if tx succeeded
    assert getStatusOfTx(tx_hash) == "success"

    # check bls keys statuses
    for key in D_valid_keys_list:
        assert key.get_status(_D) == "staked"

    # check if owner is B
    for key in D_valid_keys_list:
        assert key.belongs_to(_D)

    # === STEP 4 ============================================================
    # 4) Create a delegation contract with A

    # create contract
    tx_hash = createNewDelegationContract(_A)

    # move 5 blocks
    response = addBlocks(5)
    assert "success" in response
    # check if delegation transaction succeeded
    assert getStatusOfTx(tx_hash) == "success"

    # get delegation contract address
    DELEGATION_CONTRACT_ADDRESS = getDelegationContractAddressFromTx(tx_hash)

    # === STEP 5 ============================================================
    # 5) Merge C nodes in A's contract - should succeed
    # 5.1 - send a whitelist for merge from A to C
    tx_hash = whitelistForMerge(_A, _C, DELEGATION_CONTRACT_ADDRESS)

    # move 5 blocks
    response = addBlocks(5)
    assert "success" in response

    # check if transaction succeeded
    assert getStatusOfTx(tx_hash) == "success"

    # 5.2 - send merging tx from C
    tx_hash = mergeValidatorToDelegationWithWhitelist(_C, DELEGATION_CONTRACT_ADDRESS)

    # move 5 blocks
    response = addBlocks(5)
    assert "success" in response

    # check if transaction succeeded
    assert getStatusOfTx(tx_hash) == "success"

    time.sleep(0.5)
    # check if keys from C were transfered to A
    for key in C_valid_keys_list:
        assert key.belongs_to(_A)

    # check if keys are still staked
    for key in C_valid_keys_list:
        assert key.get_status(_A) == "staked"

    # === STEP 6 ==================================================
    # 6) Merge D nodes in A's contract - should succeed
    # 6.1 - send a whitelist for merge from A to D
    tx_hash = whitelistForMerge(_A, _D, DELEGATION_CONTRACT_ADDRESS)

    # move 5 blocks
    response = addBlocks(5)
    assert "success" in response

    # check if transaction succeeded
    assert getStatusOfTx(tx_hash) == "success"

    # 6.2 - send merging tx from A
    tx_hash = mergeValidatorToDelegationWithWhitelist(_D, DELEGATION_CONTRACT_ADDRESS)

    # move 5 blocks
    response = addBlocks(5)
    assert "success" in response

    # check if transaction succeeded
    assert getStatusOfTx(tx_hash) == "success"

    time.sleep(0.5)
    # check if keys from C were transfered to A
    for key in C_valid_keys_list:
        assert key.belongs_to(_A)

    # check if keys are still staked
    for key in C_valid_keys_list:
        assert key.get_status(_A) == "staked"

    # === STEP 7 ===============================================================
    # 7) Merge B nodes in A's contract - should fail
    # 7.1 - send a whitelist for merge from A to B
    tx_hash = whitelistForMerge(_A, _B, DELEGATION_CONTRACT_ADDRESS)

    # move 5 blocks
    response = addBlocks(5)
    assert "success" in response

    # check if transaction succeeded
    assert getStatusOfTx(tx_hash) == "success"

    # 7.2 - send merging tx from B
    tx_hash = mergeValidatorToDelegationWithWhitelist(_B, DELEGATION_CONTRACT_ADDRESS)

    # move 5 blocks
    response = addBlocks(5)
    assert "success" in response

    # check if transaction failed
    assert getStatusOfTx(tx_hash) == "failed"

    # === FINISH ===============================================================



if __name__ == '__main__':
    main()
