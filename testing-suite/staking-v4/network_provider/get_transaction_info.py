
import requests
from config import DEFAULT_PROXY
from helpers import string_to_base64
from utils.logger import logger


def get_status_of_tx(tx_hash: str) -> str:
    logger.info(f"Checking transaction status for hash: {tx_hash}")
    response = requests.get(f"{DEFAULT_PROXY}/transaction/{tx_hash}/process-status")
    response.raise_for_status()
    parsed = response.json()

    if "transaction not found" in response.text:
        return "expired"

    general_data = parsed.get("data")
    status = general_data.get("status")
    logger.info(f"Transaction status: {status} for tx_hash: {tx_hash}")
    return status


def check_if_error_is_present_in_tx(error, tx_hash) -> bool:
    logger.info(f"Checking for error in transaction {tx_hash}")
    error_bytes = string_to_base64(error)

    response = requests.get(f"{DEFAULT_PROXY}/transaction/{tx_hash}?withResults=True")
    response.raise_for_status()
    error_present = error_bytes.decode() in response.text or error in response.text
    logger.info(f"Error presence: {error_present} | in tx_hash: {tx_hash}")

    return error_present
