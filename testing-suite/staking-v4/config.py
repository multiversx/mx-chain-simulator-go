from pathlib import Path
from multiversx_sdk_network_providers import ProxyNetworkProvider

PROXY_PUBLIC_TESTNET = "https://testnet-gateway.multiversx.com"
PROXY_PUBLIC_DEVNET = "https://devnet-gateway.elrond.com"
PROXY_CHAIN_SIMULATOR = "http://localhost:8085"

DEFAULT_PROXY = PROXY_CHAIN_SIMULATOR

SYSTEM_STAKING_CONTRACT = "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqplllst77y4l"
SYSTEM_DELEGATION_MANAGER_CONTRACT = "erd1qqqqqqqqqqqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqylllslmq6y6"


proxy_default = ProxyNetworkProvider(DEFAULT_PROXY)
proxy_config = proxy_default.get_network_config()

