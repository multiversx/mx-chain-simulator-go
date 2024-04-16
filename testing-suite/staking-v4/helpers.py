import base64
from constants import *
import random
import string


def decimal_to_hex(value: int):
    hex_value = f'{value:x}'
    if len(hex_value) % 2 > 0:
        hex_value = "0" + hex_value
    return hex_value


def base64_to_hex(b):
    return base64.b64decode(b).hex()


def string_to_base64(s):
    return base64.b64encode(s.encode('utf-8'))


def base64_to_string(b):
    return base64.b64decode(b).decode('utf-8')


def replace_random_data_with_another_random_data(input_string: str) -> str:
    def generate_random_letter() -> str:
        return random.choice(string.ascii_letters)

    letter_to_be_replaced = random.choice(input_string)
    letter_to_replace_with = generate_random_letter()

    new_string = input_string.replace(letter_to_be_replaced, letter_to_replace_with)
    return new_string
