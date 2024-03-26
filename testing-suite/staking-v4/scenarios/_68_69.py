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

# extra test : Send whitelistForMerge from A to multiple addresses, and then all of them should send merge tx, nr of nodes should still be respected

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
    # AMMOUNT_TO_MINT = "50000" + "000000000000000000"
    #
    # _A = Wallet(Path("./wallets/walletKey_1.pem"))
    # _B = Wallet(Path("./wallets/walletKey_2.pem"))
    #
    # valid_key_1 = ValidatorKey(Path("./validatorKeys/validatorKey_1.pem"))
    # valid_key_2 = ValidatorKey(Path("./validatorKeys/validatorKey_2.pem"))
    # valid_key_3 = ValidatorKey(Path("./validatorKeys/validatorKey_3.pem"))
    # valid_key_4 = ValidatorKey(Path("./validatorKeys/validatorKey_4.pem"))
    #
    # _A.set_balance(AMMOUNT_TO_MINT)
    #
    # addBlocksUntilEpochReached(4)
    #
    # stake(_A, [valid_key_1, valid_key_2, valid_key_3, valid_key_4])
    #
    # addBlocks(5)


def test_68_69():
    # # TODO: generate every time a new wallet and a new validatorKey.pem
    # # TODO: create more functions for stake to avoid duplicated code and copy-paste
    # # TODO: add cli param for epochs , so we can re-run the test in different epochs for staking-v4 activation
    #
    # # === PRE-REQUIRES ==
    # # mint addresses
    # AMMOUNT_TO_MINT = "50000" + "000000000000000000"
    #
    # WALLET_A = Path("./wallets/walletKey_1.pem")
    # WALLET_B = Path("./wallets/walletKey_2.pem")
    # WALLET_C = Path("./wallets/walletKey_3.pem")
    # WALLET_D = Path("./wallets/walletKey_4.pem")
    #
    # ADDRESS_A = getPublicAddressFromPem(WALLET_A)
    # ADDRESS_B = getPublicAddressFromPem(WALLET_B)
    # ADDRESS_C = getPublicAddressFromPem(WALLET_C)
    # ADDRESS_D = getPublicAddressFromPem(WALLET_D)
    #
    # time.sleep(1)
    # response = SetEgldToAddress(AMMOUNT_TO_MINT, ADDRESS_A)
    # assert "success" in response
    # response = SetEgldToAddress(AMMOUNT_TO_MINT, ADDRESS_B)
    # assert "success" in response
    # response = SetEgldToAddress(AMMOUNT_TO_MINT, ADDRESS_C)
    # assert "success" in response
    # response = SetEgldToAddress(AMMOUNT_TO_MINT, ADDRESS_D)
    # assert "success" in response
    #
    # # add some blocks
    # response = addBlocks(5)
    # assert "success" in response
    #
    # time.sleep(1)
    # # check balances
    # assert getBalance(ADDRESS_A) == AMMOUNT_TO_MINT
    # assert getBalance(ADDRESS_B) == AMMOUNT_TO_MINT
    # assert getBalance(ADDRESS_C) == AMMOUNT_TO_MINT
    # assert getBalance(ADDRESS_D) == AMMOUNT_TO_MINT
    #
    # # go to epoch 4 , so you can stake nodes without auto-unStake them in epoch 4
    # time.sleep(1)
    # response = addBlocksUntilEpochReached("4")
    # assert "success" in response
    #
    # # === STEP 1 ===
    # # 1) Stake 4 nodes with B
    # VALIDATOR_KEY_1 = Path("./validatorKeys/validatorKey_1.pem")
    # VALIDATOR_KEY_2 = Path("./validatorKeys/validatorKey_2.pem")
    # VALIDATOR_KEY_3 = Path("./validatorKeys/validatorKey_3.pem")
    # VALIDATOR_KEY_4 = Path("./validatorKeys/validatorKey_4.pem")
    # B_valid_keys_list = [VALIDATOR_KEY_1, VALIDATOR_KEY_2, VALIDATOR_KEY_3, VALIDATOR_KEY_4]
    #
    # PUBLIC_VALIDATOR_KEY_1 = getPublicAddressFromPem(VALIDATOR_KEY_1)
    # PUBLIC_VALIDATOR_KEY_2 = getPublicAddressFromPem(VALIDATOR_KEY_2)
    # PUBLIC_VALIDATOR_KEY_3 = getPublicAddressFromPem(VALIDATOR_KEY_3)
    # PUBLIC_VALIDATOR_KEY_4 = getPublicAddressFromPem(VALIDATOR_KEY_4)
    # B_public_valid_keys_list = [PUBLIC_VALIDATOR_KEY_1, PUBLIC_VALIDATOR_KEY_2, PUBLIC_VALIDATOR_KEY_3,
    #                             PUBLIC_VALIDATOR_KEY_4]
    #
    # # stake
    # tx_hash = stake(WALLET_B, B_valid_keys_list)
    #
    # # move 5 blocks
    # response = addBlocks(5)
    # assert "success" in response
    #
    # # check if tx succeeded
    # time.sleep(1)
    # assert getStatusOfTx(tx_hash) == "success"
    #
    # # check bls keys statuses
    # ADDRESS_B_IN_HEX = Address.from_bech32(ADDRESS_B).to_hex()
    # bls_keys_status_dict = getBLSKeysStatus([ADDRESS_B_IN_HEX])
    # for pub_key in B_public_valid_keys_list:
    #     time.sleep(0.5)
    #     # TODO: after release rc/v1.7.0next1. here should be "staked"
    #     assert bls_keys_status_dict[pub_key] == "staked"
    #
    # # === STEP 2 ====
    # # 2) Stake 2 nodes with C in epoch 4
    # VALIDATOR_KEY_5 = Path("./validatorKeys/validatorKey_5.pem")
    # VALIDATOR_KEY_6 = Path("./validatorKeys/validatorKey_6.pem")
    # C_valid_keys_list = [VALIDATOR_KEY_5, VALIDATOR_KEY_6]
    #
    # PUBLIC_VALIDATOR_KEY_5 = getPublicAddressFromPem(VALIDATOR_KEY_5)
    # PUBLIC_VALIDATOR_KEY_6 = getPublicAddressFromPem(VALIDATOR_KEY_6)
    # C_public_valid_keys_list = [PUBLIC_VALIDATOR_KEY_5, PUBLIC_VALIDATOR_KEY_6]
    #
    # # stake
    # tx_hash = stake(WALLET_C, C_valid_keys_list)
    #
    # # move 5 blocks
    # response = addBlocks(5)
    # assert "success" in response
    # # check if tx succeeded
    # time.sleep(1)
    # assert getStatusOfTx(tx_hash) == "success"
    #
    # # check bls keys statuses
    # ADDRESS_C_IN_HEX = Address.from_bech32(ADDRESS_C).to_hex()
    # bls_keys_status_dict = getBLSKeysStatus([ADDRESS_C_IN_HEX])
    # for pub_key in C_public_valid_keys_list:
    #     time.sleep(0.5)
    #     # TODO: after release rc/v1.7.0next1. here should be "staked"
    #     assert bls_keys_status_dict[pub_key] == "staked"
    #
    # # === STEP 3 ====
    # # 3) Stake 2 nodes with D in epoch 4
    # VALIDATOR_KEY_7 = Path("./validatorKeys/validatorKey_7.pem")
    # VALIDATOR_KEY_8 = Path("./validatorKeys/validatorKey_8.pem")
    # D_valid_keys_list = [VALIDATOR_KEY_7, VALIDATOR_KEY_8]
    #
    # PUBLIC_VALIDATOR_KEY_7 = getPublicAddressFromPem(VALIDATOR_KEY_7)
    # PUBLIC_VALIDATOR_KEY_8 = getPublicAddressFromPem(VALIDATOR_KEY_8)
    # D_public_valid_keys_list = [PUBLIC_VALIDATOR_KEY_7, PUBLIC_VALIDATOR_KEY_8]
    #
    # # stake
    # tx_hash = stake(WALLET_D, D_valid_keys_list)
    #
    # # move 5 blocks
    # response = addBlocks(5)
    # assert "success" in response
    # time.sleep(1)
    # # check if tx succeeded
    # assert getStatusOfTx(tx_hash) == "success"
    #
    # # TODO: add a function like : checkOwnerOfBlsKeys(owner, bls_keys:List[]) and checkStatusOfBlsKeys()
    # # check bls keys statuses
    # ADDRESS_D_IN_HEX = Address.from_bech32(ADDRESS_D).to_hex()
    # bls_keys_status_dict = getBLSKeysStatus([ADDRESS_D_IN_HEX])
    # for pub_key in D_public_valid_keys_list:
    #     time.sleep(0.5)
    #     # TODO: after release rc/v1.7.0next1. here should be "staked"
    #     assert bls_keys_status_dict[pub_key] == "staked"
    #
    # # === STEP 4 ===
    # # 4) Create a delegation contract with A
    # # create contract
    # tx_hash = createNewDelegationContract(Path(WALLET_A))
    # # move 5 blocks
    # response = addBlocks(5)
    # assert "success" in response
    # # check if delegation transaction succeeded
    # assert getStatusOfTx(tx_hash) == "success"
    # # get delegation contract address
    # DELEGATION_CONTRACT_ADDRESS = getDelegationContractAddressFromTx(tx_hash)
    #
    # # === STEP 5 ===
    # # 5) Merge C nodes in A's contract - should succeed
    # # 5.1 - send a whitelist for merge from C to A
    # tx_hash = whitelistForMerge(WALLET_C, DELEGATION_CONTRACT_ADDRESS, ADDRESS_A)
    #
    # # move 5 blocks
    # response = addBlocks(5)
    # assert "success" in response
    #
    # # check if transaction succeeded
    # assert getStatusOfTx(tx_hash) == "success"
    #
    # # 5.2 - send merging tx from A to C
    # tx_hash = mergeValidatorToDelegationWithWhitelist(WALLET_A, DELEGATION_CONTRACT_ADDRESS)
    #
    # # move 5 blocks
    # response = addBlocks(5)
    # assert "success" in response
    #
    # # check if transaction succeeded
    # assert getStatusOfTx(tx_hash) == "success"
    #
    # # check if keys from C were transfered to A
    # ADDRESS_A_IN_HEX = Address.from_bech32(ADDRESS_A).to_hex()
    # bls_keys_status_dict = getBLSKeysStatus([ADDRESS_A_IN_HEX])
    # for pub_key in C_public_valid_keys_list:
    #     time.sleep(0.5)
    #     # TODO: after release rc/v1.7.0next1. here should be "staked"
    #     assert bls_keys_status_dict[pub_key] == "staked"

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
