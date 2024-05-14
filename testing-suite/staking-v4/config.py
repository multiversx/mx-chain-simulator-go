from pathlib import Path
from multiversx_sdk_network_providers import ProxyNetworkProvider


PROXY_PUBLIC_TESTNET = "https://testnet-gateway.multiversx.com"
PROXY_PUBLIC_DEVNET = "https://devnet-gateway.multiversx.com"
PROXY_CHAIN_SIMULATOR = "http://localhost:8085"

DEFAULT_PROXY = PROXY_CHAIN_SIMULATOR

# TEMP
OBSERVER_META = "http://localhost:55802"

try:
    proxy_default = ProxyNetworkProvider(DEFAULT_PROXY)
except:
    Exception

chain_id = "chain"

# relative path to chain-simulator
chain_simulator_path = Path("../../cmd/chainsimulator")

# config for cli flags for starting chain simulator
log_level = '"*:DEBUG,process:TRACE"'
num_validators_per_shard = "10"
num_validators_meta = "10"
num_waiting_validators_per_shard = "6"
num_waiting_validators_meta = "6"
# real config after staking v4 full activation: eligible = 10 *4 , waiting = (6-2) *4, qualified =  2*4
# qualified nodes from auction will stay in wiating 2 epochs

rounds_per_epoch = "50"
