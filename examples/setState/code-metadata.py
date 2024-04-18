import sys
import time
from pathlib import Path
from typing import Any, Dict, Sequence

from multiversx_sdk_core import TokenComputer, AddressFactory
from multiversx_sdk_core.transaction_factories import TransactionsFactoryConfig, TokenManagementTransactionsFactory, \
    TransferTransactionsFactory
from multiversx_sdk_network_providers import ProxyNetworkProvider
from multiversx_sdk_wallet import UserPEM

SIMULATOR_URL = "http://localhost:8085"
GENERATE_BLOCKS_URL = f"{SIMULATOR_URL}/simulator/generate-blocks"
SET_STATE_URL = f"{SIMULATOR_URL}/simulator/set-state"
ADDRESS_URL = f"{SIMULATOR_URL}/address/"

def main():
    provider = ProxyNetworkProvider(SIMULATOR_URL)

    test_state: Sequence[Dict[str, Any]] = [
        {
            'address': 'erd1qyqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqlqnj4d', # invalid SC address
            'nonce': 0,
            'balance': '1000000000000000000',
            'keys': {'454c524f4e44657364744646542d616263646566': '1209000de0b6b3a7640000'},
            'code': '',
            'codeMetadata': 'BAA=',
            'ownerAddress': '',
            'developerReward': '0'
        },
        {
            'address': 'erd1qqqqqqqqqqqqqpgqjsnxqprks7qxfwkcg2m2v9hxkrchgm9akp2segrswt', # valid SC address
            'nonce': 0,
            'balance': '1000000000000000000',
            'keys': {'454c524f4e44657364744646542d616263646566': '1209000de0b6b3a7640000'},
            'code': '',
            'codeMetadata': 'BAA=',
            'ownerAddress': '',
            'developerReward': '0'
        }]

    provider.do_post(SET_STATE_URL, test_state)

    num_blocks_to_generate = 10
    provider.do_post(f"{GENERATE_BLOCKS_URL}/{num_blocks_to_generate}", {})

    # for this address the code metadata should be empty as the address is not a valid SC address
    response = provider.do_get_generic(f'address/erd1qyqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqlqnj4d')
    account_response = response.get("account")
    code_metadata = account_response.get('codeMetadata', '')
    if code_metadata != '':
        sys.exit(f"code metadata is not empty")

    # for this address the code metadata should be set as the address is a valid SC address
    response = provider.do_get_generic(f'address/erd1qqqqqqqqqqqqqpgqjsnxqprks7qxfwkcg2m2v9hxkrchgm9akp2segrswt')
    account_response = response.get("account")
    code_metadata = account_response.get('codeMetadata', '')
    if code_metadata != 'BAA=':
        sys.exit(f"code metadata is different from 'BAA='")


if __name__ == "__main__":
    main()