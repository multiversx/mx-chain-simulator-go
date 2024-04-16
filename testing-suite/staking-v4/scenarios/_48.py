import threading

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
from core.chain_simulator import *
from threading import Thread

# Steps:
# 1) Stake with A 2 nodes
# 2) check if balance is - (5000 + gas fees)
# 3) check with getTotalStaked that has 5000 egld staked
# 4) check with getOwner if staked keys belongs to A
# 5) check with getBlsKeysStatus if keys are staked
# do this in epoch 3, 4, 5 and 6


EPOCHS = [3, 4, 5, 6]
blockchain = ChainSimulator(chain_simulator_path)


def chain_start():
    print("chain is starting...")
    blockchain.start()


def main():
    print("Happy testing")


def test_48():

    def scenario(epoch: int):

        if is_chain_online():
            # === PRE-CONDITIONS ==============================================================
            AMMOUNT_TO_MINT = "6000" + "000000000000000000"

            _A = Wallet(Path("./wallets/walletKey_1.pem"))

            # check if minting is successful
            assert "success" in _A.set_balance(AMMOUNT_TO_MINT)

            # add some blocks
            response = addBlocks(5)
            assert "success" in response
            time.sleep(0.5)

            # check balance
            assert _A.get_balance() == AMMOUNT_TO_MINT

            # move to epoch
            assert "success" in addBlocksUntilEpochReached(epoch)

            # === STEP 1 ==============================================================
            # 1) Stake with A 2 nodes
            VALIDATOR_KEY_1 = ValidatorKey(Path("./validatorKeys/validatorKey_1.pem"))
            VALIDATOR_KEY_2 = ValidatorKey(Path("./validatorKeys/validatorKey_2.pem"))
            A_Keys = [VALIDATOR_KEY_1, VALIDATOR_KEY_2]

            tx_hash = stake(_A, A_Keys)

            # move few blocks and check tx
            assert addBlocksUntilTxSucceeded(tx_hash) == "success"

            # === STEP 2 ==============================================================
            # 2) check balance of A to be - (5000+gas fees)
            assert int(_A.get_balance()) < int(AMMOUNT_TO_MINT) - 5000

            # === STEP 3 ==============================================================
            # 3) check total stake of A
            total_staked = getTotalStaked(_A.public_address())
            assert total_staked == "5000" + "000000000000000000"

            # === STEP 4 ==============================================================
            # 4) check owner of keys
            for key in A_Keys:
                assert key.belongs_to(_A.public_address())

            # === STEP 5 ==============================================================
            # 5) check with getBlsKeysStatus if keys are staked or queued if epoch 3
            for key in A_Keys:
                if epoch == 3:
                    assert key.get_status(_A.public_address()) == "queued"
                else:
                    assert key.get_status(_A.public_address()) == "staked"

            # make sure all checks were done in needed epoch
            assert proxy_default.get_network_status().epoch_number == epoch
            # === FINISH ===============================================================

            # stop chain
            blockchain.stop()

    # loop through all epochs needed for this scenario
    for epoch in EPOCHS:
        print(f"======================== EPOCH {epoch} =================================")
        t1 = threading.Thread(target=chain_start)
        t2 = threading.Thread(target=scenario, args=(epoch,))

        t1.start(), t2.start()
        t1.join(), t2.join()


if __name__ == '__main__':
    main()
