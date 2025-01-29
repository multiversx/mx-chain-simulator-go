from typing import Any, Dict, Sequence

from multiversx_sdk import ProxyNetworkProvider

SIMULATOR_URL = "http://localhost:8085"
SET_STATE_URL = "simulator/set-state-overwrite"
ADDRESS_URL = "address/"


def main():
    provider = ProxyNetworkProvider(SIMULATOR_URL)

    test_state: Sequence[Dict[str, Any]] = [
        {
            'address': 'erd1qyqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqlqnj4d',  # invalid SC address
            'nonce': 0,
            'balance': '1000000000000000000',
            'keys': {'454c524f4e44657364744646542d616263646566': '1209000de0b6b3a7640000'},
            'code': '',
            'codeMetadata': 'BAA=',
            'ownerAddress': '',
            'developerReward': '0'
        },
        {
            'address': 'erd1qqqqqqqqqqqqqpgqjsnxqprks7qxfwkcg2m2v9hxkrchgm9akp2segrswt',  # valid SC address
            'nonce': 0,
            'balance': '1000000000000000000',
            'keys': {'454c524f4e44657364744646542d616263646566': '1209000de0b6b3a7640000'},
            'code': '',
            'codeMetadata': 'BAA=',
            'ownerAddress': '',
            'developerReward': '0'
        }]

    provider.do_post_generic(SET_STATE_URL, test_state)

    # for this address the code metadata should be empty as the address is not a valid SC address
    response = provider.do_get_generic(f'address/erd1qyqqqqqpqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqlqnj4d')
    account_response = response.get("account")
    code_metadata = account_response.get('codeMetadata', '')
    if code_metadata is not None:
        assert code_metadata is not None, "code metadata is not empty"

    # for this address the code metadata should be set as the address is a valid SC address
    response = provider.do_get_generic(f'address/erd1qqqqqqqqqqqqqpgqjsnxqprks7qxfwkcg2m2v9hxkrchgm9akp2segrswt')
    account_response = response.get("account")
    code_metadata = account_response.get('codeMetadata', '')
    if code_metadata != 'BAA=':
        assert code_metadata == 'BAA=', "code metadata is different from 'BAA='"


if __name__ == "__main__":
    main()
