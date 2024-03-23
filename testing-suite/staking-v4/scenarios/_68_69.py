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


def main():
    print("Happy testing")


def test_68_69():
    # TODO: generate every time a new wallet and a new validatorKey.pem
    # TODO: create more functions for stake to avoid duplicated code and copy-paste
    # TODO: add cli param for epochs , so we can re-run the test in different epochs for staking-v4 activation

    # === PRE-REQUIRES ==
    # mint addresses
    AMMOUNT_TO_MINT = "50000" + "000000000000000000"

    WALLET_A = Path("./wallets/walletKey_1.pem")
    WALLET_B = Path("./wallets/walletKey_2.pem")
    WALLET_C = Path("./wallets/walletKey_3.pem")
    WALLET_D = Path("./wallets/walletKey_4.pem")

    ADDRESS_A = getPublicAddressFromPem(WALLET_A)
    ADDRESS_B = getPublicAddressFromPem(WALLET_B)
    ADDRESS_C = getPublicAddressFromPem(WALLET_C)
    ADDRESS_D = getPublicAddressFromPem(WALLET_D)

    time.sleep(1)
    response = SetEgldToAddress(AMMOUNT_TO_MINT, ADDRESS_A)
    assert "success" in response
    response = SetEgldToAddress(AMMOUNT_TO_MINT, ADDRESS_B)
    assert "success" in response
    response = SetEgldToAddress(AMMOUNT_TO_MINT, ADDRESS_C)
    assert "success" in response
    response = SetEgldToAddress(AMMOUNT_TO_MINT, ADDRESS_D)
    assert "success" in response

    # add some blocks
    response = addBlocks(5)
    assert "success" in response

    time.sleep(1)
    # check balances
    assert getBalance(ADDRESS_A) == AMMOUNT_TO_MINT
    assert getBalance(ADDRESS_B) == AMMOUNT_TO_MINT
    assert getBalance(ADDRESS_C) == AMMOUNT_TO_MINT
    assert getBalance(ADDRESS_D) == AMMOUNT_TO_MINT

    # go to epoch 4 , so you can stake nodes without auto-unStake them in epoch 4
    time.sleep(1)
    response = addBlocksUntilEpochReached("4")
    assert "success" in response

    # === STEP 1 ===
    # 1) Stake 4 nodes with B
    VALIDATOR_KEY_1 = Path("./validatorKeys/validatorKey_1.pem")
    VALIDATOR_KEY_2 = Path("./validatorKeys/validatorKey_2.pem")
    VALIDATOR_KEY_3 = Path("./validatorKeys/validatorKey_3.pem")
    VALIDATOR_KEY_4 = Path("./validatorKeys/validatorKey_4.pem")
    B_valid_keys_list = [VALIDATOR_KEY_1, VALIDATOR_KEY_2, VALIDATOR_KEY_3, VALIDATOR_KEY_4]

    PUBLIC_VALIDATOR_KEY_1 = getPublicAddressFromPem(VALIDATOR_KEY_1)
    PUBLIC_VALIDATOR_KEY_2 = getPublicAddressFromPem(VALIDATOR_KEY_2)
    PUBLIC_VALIDATOR_KEY_3 = getPublicAddressFromPem(VALIDATOR_KEY_3)
    PUBLIC_VALIDATOR_KEY_4 = getPublicAddressFromPem(VALIDATOR_KEY_4)
    B_public_valid_keys_list = [PUBLIC_VALIDATOR_KEY_1, PUBLIC_VALIDATOR_KEY_2, PUBLIC_VALIDATOR_KEY_3,
                              PUBLIC_VALIDATOR_KEY_4]

    # stake
    tx_hash = stake(WALLET_B, B_valid_keys_list)

    # move 5 blocks
    response = addBlocks(5)
    assert "success" in response

    time.sleep(1)
    assert getStatusOfTx(tx_hash) == "success"

    # check bls keys statuses
    ADDRESS_B_IN_HEX = Address.from_bech32(ADDRESS_B).to_hex()
    bls_keys_status_dict = getBLSKeysStatus([ADDRESS_B_IN_HEX])
    for pub_key in B_public_valid_keys_list:
        time.sleep(0.5)
        # TODO: after release rc/v1.7.0next1. here should be "staked"
        assert bls_keys_status_dict[pub_key] == "queued"


    # === STEP 2 ====
    # 2) Stake 2 nodes with C in epoch 4
    VALIDATOR_KEY_5 = Path("./validatorKeys/validatorKey_5.pem")
    VALIDATOR_KEY_6 = Path("./validatorKeys/validatorKey_6.pem")
    C_valid_keys_list = [VALIDATOR_KEY_5, VALIDATOR_KEY_5]

    PUBLIC_VALIDATOR_KEY_5 = getPublicAddressFromPem(VALIDATOR_KEY_5)
    PUBLIC_VALIDATOR_KEY_6 = getPublicAddressFromPem(VALIDATOR_KEY_6)
    C_public_valid_keys_list = [PUBLIC_VALIDATOR_KEY_5, PUBLIC_VALIDATOR_KEY_6]

    # stake
    tx_hash = stake(WALLET_C, C_valid_keys_list)

    # move 5 blocks
    response = addBlocks(5)
    assert "success" in response

    time.sleep(1)
    assert getStatusOfTx(tx_hash) == "success"

    # check bls keys statuses
    ADDRESS_C_IN_HEX = Address.from_bech32(ADDRESS_C).to_hex()
    bls_keys_status_dict = getBLSKeysStatus([ADDRESS_C_IN_HEX])
    for pub_key in C_public_valid_keys_list:
        time.sleep(0.5)
        # TODO: after release rc/v1.7.0next1. here should be "staked"
        assert bls_keys_status_dict[pub_key] == "queued"


    # === STEP 3 ====
    # 3) Stake 2 nodes with D in epoch 4
    VALIDATOR_KEY_7 = Path("./validatorKeys/validatorKey_7.pem")
    VALIDATOR_KEY_8 = Path("./validatorKeys/validatorKey_8.pem")
    D_valid_keys_list = [VALIDATOR_KEY_7, VALIDATOR_KEY_8]

    PUBLIC_VALIDATOR_KEY_7 = getPublicAddressFromPem(VALIDATOR_KEY_7)
    PUBLIC_VALIDATOR_KEY_8 = getPublicAddressFromPem(VALIDATOR_KEY_8)
    D_public_valid_keys_list = [PUBLIC_VALIDATOR_KEY_7, PUBLIC_VALIDATOR_KEY_8]

    # stake
    tx_hash = stake(WALLET_D, D_valid_keys_list)

    # move 5 blocks
    response = addBlocks(5)
    assert "success" in response

    time.sleep(1)
    assert getStatusOfTx(tx_hash) == "success"

    # check bls keys statuses
    ADDRESS_D_IN_HEX = Address.from_bech32(ADDRESS_D).to_hex()
    bls_keys_status_dict = getBLSKeysStatus([ADDRESS_D_IN_HEX])
    for pub_key in D_public_valid_keys_list:
        time.sleep(0.5)
        # TODO: after release rc/v1.7.0next1. here should be "staked"
        assert bls_keys_status_dict[pub_key] == "queued"


    # === STEP 4 ===
    # 4) Create a delegation contract with A
    # create contract
    tx_hash = createNewDelegationContract(Path(WALLET_A))

    # move 5 blocks
    response = addBlocks(5)
    assert "success" in response

    # check if delegation transaction succeeded
    assert getStatusOfTx(tx_hash) == "success"

    # get delegation contract address
    DELEGATION_CONTRACT_ADDRESS = getDelegationContractAddressFromTx(tx_hash)



if __name__ == '__main__':
    main()
