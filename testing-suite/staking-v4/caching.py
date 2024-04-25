import requests
from config import DEFAULT_PROXY
from chain_commander import add_blocks


def force_reset_validator_statistics():
    route = f"{DEFAULT_PROXY}/simulator/force-reset-validator-statistics"
    response = requests.post(route)
    response.raise_for_status()

    # add an extra block
    response = add_blocks(1)



