import time

from core.wallet import Wallet
from core.validatorKey import ValidatorKey
from chain_commander import add_blocks, add_blocks_until_epoch_reached, add_blocks_until_tx_fully_executed, \
    is_chain_online
from network_provider.key_management import add_key
from pathlib import Path
from delegation import create_new_delegation_contract, merge_validator_to_delegation_same_owner, \
    merge_validator_to_delegation_with_whitelist, whitelist_for_merge
from network_provider.get_delegation_info import get_delegation_contract_address_from_tx
from delegation import add_nodes, stake_nodes
from staking import stake
import pytest

# General :
# In this scenario we will test all posibilities of creating delegation contracts, and test that
# every contract will work properly (happy path) with users interactions: delegate, undelegate, claim, nodes merging etc
# We will run the scenario starting with epoch 3 , 4 and 5.

# Steps:
# 1) In epoch x create 6 users. Each user will be creating a delegation contract in a diferent way / diferent context
# All users will create the contract with fixed delegation cap of 10000 egld and with 10% service fee using 2 keys.
#   1.1) User A - will use createNewDelegationContract function
#   1.2) User B - will use createNewDelegationContract function, but the second node will be added
#   with mergeValidatorToDelegationSameOwner
#   1.3) User C - will use createNewDelegationContract function, but the second node will be added
#   with whitelistForMerge
#   1.4) User D - will use makeNewContractFromValidatorData function
#   1.5) User F - will use makeNewContractFromValidatorData function, but the second node will be added
#   with mergeValidatorToDelegationSameOwner
#   1.6) User G - will use makeNewContractFromValidatorData function, but the second node will be added
#   with whitelistForMerge
# 2) In epoch x create 6 delegators that will delegate 1 egld to each user. After each delegation check that:
#   2.1) Balance of the delegator decreased with 1 egld + transaction fee
#   2.2) Check with getTotalActiveStake vm-query that the account has 1 egld staked.
#   2.3) Check with getTotalStaked vm-query that the SP contract stake has increased with 1 egld.
# 3) Create 1 temp delegator that will only test that the delegation cap of each contract will not be overfulfilled
# 4) In epoch x+10 check rewards for each delegator and should not be very big differences.
# 5) In epoch x+10 redelegate rewards with all delegators.
# 6) In epoch x+20 check rewards for each delegator and should not be very big differences.
# 7) In epoch x+20 claim rewards with all delegators
# 8) In epoch x+20 undelegate everything with all delegators
# 9) In epoch x+20 withdraw all with all delegators

EPOCHS_ID = [3, 4, 5, 6]


def epoch_id(val):
    return f"EPOCH-{val}"


def main():
    print("Happy testing")


@pytest.mark.parametrize("epoch", EPOCHS_ID, indirect=True, ids=epoch_id)
def test_70_75_validator_to_sp_transitions_and_validations(blockchain, epoch):
    # === PRE-CONDITIONS ==============================================================
    assert True == is_chain_online()

    # mint addresses
    AMOUNT_TO_MINT = "6000" + "000000000000000000"
    AMOUNT_FOR_SECONDARY_WALLET = "30000" + "000000000000000000"

    _A = Wallet(Path("./wallets/walletKey_1.pem"))
    key_1 = ValidatorKey(Path("./validatorKeys/validatorKey_1.pem"))
    key_2 = ValidatorKey(Path("./validatorKeys/validatorKey_2.pem"))
    A_keys = [key_1, key_2]

    _B = Wallet(Path("./wallets/walletKey_2.pem"))
    key_3 = ValidatorKey(Path("./validatorKeys/validatorKey_3.pem"))
    key_4 = ValidatorKey(Path("./validatorKeys/validatorKey_4.pem"))
    B_keys = [key_3, key_4]

    _C = Wallet(Path("./wallets/walletKey_3.pem"))
    key_5 = ValidatorKey(Path("./validatorKeys/validatorKey_5.pem"))
    key_6 = ValidatorKey(Path("./validatorKeys/validatorKey_6.pem"))
    C_keys = [key_5, key_6]

    _D = Wallet(Path("./wallets/walletKey_4.pem"))
    key_7 = ValidatorKey(Path("./validatorKeys/validatorKey_7.pem"))
    key_8 = ValidatorKey(Path("./validatorKeys/validatorKey_8.pem"))
    D_keys = [key_7, key_8]

    _E = Wallet(Path("./wallets/walletKey_5.pem"))
    key_9 = ValidatorKey(Path("./validatorKeys/validatorKey_9.pem"))
    key_10 = ValidatorKey(Path("./validatorKeys/validatorKey_10.pem"))
    E_keys = [key_9, key_10]

    _F = Wallet(Path("./wallets/walletKey_6.pem"))
    key_11 = ValidatorKey(Path("./validatorKeys/validatorKey_11.pem"))
    key_12 = ValidatorKey(Path("./validatorKeys/validatorKey_12.pem"))
    F_keys = [key_11, key_12]

    _G = Wallet(Path("./wallets/walletKey_7.pem"))
    all_keys = A_keys + B_keys + C_keys + D_keys + E_keys + F_keys

    # check minting request will succeed
    assert "success" in _A.set_balance(AMOUNT_TO_MINT)
    assert "success" in _B.set_balance(AMOUNT_TO_MINT)
    assert "success" in _C.set_balance(AMOUNT_TO_MINT)
    assert "success" in _D.set_balance(AMOUNT_TO_MINT)
    assert "success" in _E.set_balance(AMOUNT_TO_MINT)
    assert "success" in _F.set_balance(AMOUNT_TO_MINT)
    assert "success" in _G.set_balance(AMOUNT_FOR_SECONDARY_WALLET)

    # add some blocks
    response = add_blocks(5)
    assert "success" in response

    # check balances
    assert _A.get_balance() == AMOUNT_TO_MINT
    assert _B.get_balance() == AMOUNT_TO_MINT
    assert _C.get_balance() == AMOUNT_TO_MINT
    assert _D.get_balance() == AMOUNT_TO_MINT
    assert _E.get_balance() == AMOUNT_TO_MINT
    assert _F.get_balance() == AMOUNT_TO_MINT
    assert _G.get_balance() == AMOUNT_FOR_SECONDARY_WALLET

    # add all keys to protocol so they will be not jailed
    assert "success" in add_key(all_keys)

    # go to needed epoch
    response = add_blocks_until_epoch_reached(epoch)
    assert "success" in response

    # === STEP 1 ===============================================================
    # 1) In epoch x create 6 users. Each user will be creating a delegation contract in a diferent way/diferent context
    # All users will create the contract with fixed delegation cap of 10000 egld and with 10% service fee using 2 keys.
    #   1.1) User A - will use createNewDelegationContract function

    tx_hash = create_new_delegation_contract(_A, AMOUNT="5000000000000000000000", SERVICE_FEE="03e8",
                                             DELEGATION_CAP="021e19e0c9bab2400000")
    assert add_blocks_until_tx_fully_executed(tx_hash) == "success"

    SP_address_for_A = get_delegation_contract_address_from_tx(tx_hash)

    tx_hash = add_nodes(_A, SP_address_for_A, A_keys)
    assert add_blocks_until_tx_fully_executed(tx_hash) == "success"

    tx_hash = stake_nodes(_A, SP_address_for_A, A_keys)
    assert add_blocks_until_tx_fully_executed(tx_hash) == "success"

    # check if nodes are staked
    for key in A_keys:
        assert key.get_status(SP_address_for_A) == "staked"

    #   1.2) User B - will use createNewDelegationContract function, but the second node will be added
    #   with mergeValidatorToDelegationSameOwner

    tx_hash = create_new_delegation_contract(_B, AMOUNT="2500000000000000000000", SERVICE_FEE="03e8",
                                             DELEGATION_CAP="021e19e0c9bab2400000")
    assert add_blocks_until_tx_fully_executed(tx_hash) == "success"

    SP_address_for_B = get_delegation_contract_address_from_tx(tx_hash)

    # add and stake_nodes only 1 key, the other will be added with mergeValidatorToDelegationSameOwner
    tx_hash = add_nodes(_B, SP_address_for_B, [B_keys[0]])
    assert add_blocks_until_tx_fully_executed(tx_hash) == "success"

    tx_hash = stake_nodes(_B, SP_address_for_B, [B_keys[0]])
    assert add_blocks_until_tx_fully_executed(tx_hash) == "success"

    # check if the node is staked
    assert B_keys[0].get_status(SP_address_for_B) == "staked"

    # stake the other key, but not through the delegation contract
    tx_hash = stake(_B, [B_keys[1]])
    assert add_blocks_until_tx_fully_executed(tx_hash) == "success"

    # check if the node is staked
    assert B_keys[1].get_status(_B.public_address()) == "staked"

    # merge the normal staked key with the delegation contract
    tx_hash = merge_validator_to_delegation_same_owner(_B, SP_address_for_B)
    assert add_blocks_until_tx_fully_executed(tx_hash) == "success"

    # check if the new owner is now the delegation contract
    assert B_keys[1].belongs_to(SP_address_for_B)


if __name__ == '__main__':
    main()
