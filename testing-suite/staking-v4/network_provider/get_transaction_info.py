
import requests
from config import DEFAULT_PROXY
from helpers import string_to_base64


def get_status_of_tx(tx_hash: str) -> str:
    response = requests.get(f"{DEFAULT_PROXY}/transaction/{tx_hash}/process-status")
    response.raise_for_status()
    parsed = response.json()

    if "transaction not found" in response.text:
        return "expired"

    general_data = parsed.get("data")
    status = general_data.get("status")
    return status


def check_if_error_is_present_in_tx(error, tx_hash) -> bool:
    error_bytes = string_to_base64(error)

    response = requests.get(f"{DEFAULT_PROXY}/transaction/{tx_hash}?withResults=True")
    response.raise_for_status()

    return error_bytes.decode() in response.text or error in response.text
