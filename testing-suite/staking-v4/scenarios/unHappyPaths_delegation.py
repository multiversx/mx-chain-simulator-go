

# General:
# here will be tested most of the cases that should fail regarding interaction with stakign providers

# Steps:
# 1) Create a new delegation contract with "createNewDelegationContract" function with less than 1250 egld.
#   1.1) Tx should fail
#   1.2) Check that wallet balance is the same like before sending the tx - gass fees
#   1.3) Check te error message after sending the tx
# 2) Create a new delegation contract with 1250 egld with 0% fees and 4900 egld delegation cap - tx should pass
# 3) Add a new key to the contract
# 4) Stake a key to the contract that is not added
#   4.1) Tx should fail
#   4.2) Check error of the tx
# 5) Stake the key from point 3)
#   5.1) Tx should fail
#   5.2) Check error of tx
# 6) Delegate with another user 1250 egld to the contract
# 7) Stake the key from point 3) - now tx should pass




