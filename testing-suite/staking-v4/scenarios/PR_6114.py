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

# SCENARIO 1
# Have every epoch auction list with enough nodes (let's say 8 qualified, 2 unqualified)
# Unstake 1 or more eligible/waiting nodes (no more than all nodes per shard or no more than all eligible)
# and call auction list api; we should see 8 qualified nodes. Next epoch we need to check that exactly 8 nodes were qualified.
# Afterwards(some epochs), those leaving nodes will be leaving and replaced by the auction nodes

def main():



if __name__ == '__main__':
    main()