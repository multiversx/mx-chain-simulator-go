import requests
from config import DEFAULT_PROXY


def force_reset_validator_statistics():
    route = f"{DEFAULT_PROXY}/simulator/force-reset-validator-statistics"
    response = requests.post(route)
    response.raise_for_status()

