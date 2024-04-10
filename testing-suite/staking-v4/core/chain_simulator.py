import stat

from constants import *
from config import *
import os
import signal
import subprocess
from subprocess import Popen
from threading import Thread
import threading


class ChainSimulator:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.log_level = log_level
        self.num_validators_per_shard = num_validators_per_shard
        self.num_validators_meta = num_validators_meta
        self.num_waiting_validators_per_shard = num_waiting_validators_per_shard
        self.num_waiting_validators_meta = num_waiting_validators_meta
        self.process = None

    def start(self):
        command = f"./chainsimulator --log-level {self.log_level} \
                                    -num-validators-per-shard {self.num_validators_per_shard} \
                                    -num-waiting-validators-per-shard {num_waiting_validators_per_shard} \
                                    -num-validators-meta {num_validators_meta} \
                                    -num-waiting-validators-meta {num_waiting_validators_meta}"
        flag = True
        while flag:
            if "  " in command:
                command = command.replace("  ", " ")
            else:
                flag = False
        print(command)

        self.process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                        shell=True, preexec_fn=os.setsid, cwd=chain_simulator_path)

        out, err = self.process.communicate()
        if err:
            print(err)

    def stop(self) -> None:
        self.process.terminate()


