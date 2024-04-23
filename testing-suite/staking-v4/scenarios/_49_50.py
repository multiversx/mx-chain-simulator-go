import threading

from get_infos.get_transaction_info import check_if_error_is_present_in_tx
from chain_commander import *
from staking import *
from core.validatorKey import *
from core.chain_simulator import *


# Steps
# 1) Test 49 : Stake a node with an invalid bls key
# 2) Test 49.1 : Stake a node with an already staked bls key
# 3) Test 50 : Stake a node with less than 2500 egld


EPOCHS = [3, 4, 5, 6]
blockchain = ChainSimulator(chain_simulator_path)


def chain_start():
    print("chain is starting...")
    blockchain.start()


def main():
    print("Happy testing")


def test_49_50():

    def scenario(epoch: int):

        if is_chain_online():
            # === PRE-CONDITIONS ==============================================================
            AMOUNT_TO_MINT = "6000" + "000000000000000000"

            _A = Wallet(Path("./wallets/walletKey_1.pem"))
            _B = Wallet(Path("./wallets/walletKey_2.pem"))
            _C = Wallet(Path("./wallets/walletKey_3.pem"))

            # check if minting is successful
            assert "success" in _A.set_balance(AMOUNT_TO_MINT)
            assert "success" in _B.set_balance(AMOUNT_TO_MINT)
            assert "success" in _C.set_balance(AMOUNT_TO_MINT)

            # add some blocks
            response = add_blocks(5)
            assert "success" in response
            time.sleep(0.5)

            # check balance
            assert _A.get_balance() == AMOUNT_TO_MINT
            assert _B.get_balance() == AMOUNT_TO_MINT
            assert _C.get_balance() == AMOUNT_TO_MINT

            # move to epoch
            assert "success" in add_blocks_until_epoch_reached(epoch)

            # === STEP 1 ==============================================================
            # 1) Test 49 : Stake a node with an invalid bls key

            # BEGIN #########################################################################
            # THIS CODE IS COMMETED BECAUSE AFTER MULTIPLE TRIES IT IS NOT POSIBLE TO TEST ON CHAIN SIMULATOR
            # THIS SCENARIO BECAUSE SIGNATURES DOES NOT MATTER , WE LEFT THE CODE HERE FOR FUTURE TESTING ON TESTNETS
            # invalid_key = ValidatorKey(Path("./validatorKeys/invalid_bls_key_1.pem"))
            # normal_key = ValidatorKey(Path("./validatorKeys/validatorKey_1.pem"))
            #
            # # move few blocks and check tx , the py framework should fail the decoding because of the wrong bls key file
            # # this way we test the framework too
            # try:
            #     tx_hash = stake(_A, [invalid_key])
            # except Exception as error:
            #     print(error)
            #     assert "codec can't decode byte" in str(error)
            #
            # # send a malicious stake with wrong stake signature / public key / nr of nodes
            # tx_hash = malicious_stake(_A, [normal_key], TX_DATA_MANIPULATOR=True)
            #
            # assert addBlocksUntilTxSucceeded(tx_hash) == "fail"
            # END ############################################################################

            # === STEP 2 ==============================================================
            # 2) Test 49.1 : Stake a node with an already staked bls key
            # stake a key for the first time
            _key = ValidatorKey(Path("./validatorKeys/validatorKey_2.pem"))
            tx_hash = stake(_A, [_key])

            assert add_blocks_until_tx_fully_executed(tx_hash) == "success"

            # make sure key is staked
            if epoch == 3:
                assert _key.get_status(_A.public_address()) == "queued"
            else:
                assert _key.get_status(_A.public_address()) == "staked"

            # stake same key again
            tx_hash = stake(_B, [_key])

            assert add_blocks_until_tx_fully_executed(tx_hash) == "fail"

            # check if it fails with the correct error message
            assert check_if_error_is_present_in_tx("error bls key already registered", tx_hash)

            # === STEP 3 ==============================================================
            # 3) Test 50 : Stake a node with less than 2500 egld
            # send a malicious stake with less than 2500 egld
            _key = ValidatorKey(Path("./validatorKeys/validatorKey_3.pem"))
            tx_hash = malicious_stake(_C, [_key], AMOUNT_DEFICIT=1)

            assert add_blocks_until_tx_fully_executed(tx_hash) == "fail"

            # check if error message is present in tx
            assert check_if_error_is_present_in_tx("insufficient stake value", tx_hash)

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
