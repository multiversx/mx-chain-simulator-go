import base64
from constants import *
import random
import string


def decimalToHex(value: int):
    hex_value = f'{value:x}'
    if len(hex_value) % 2 > 0:
        hex_value = "0" + hex_value
    return hex_value


def base64ToHex(b):
    return base64.b64decode(b).hex()


def stringToBase64(s):
    return base64.b64encode(s.encode('utf-8'))


def base64ToString(b):
    return base64.b64decode(b).decode('utf-8')


def replaceRandomDataWithAnotherRandomData(input_string: str) -> str:
    def generateRandomLetter() -> str:
        return random.choice(string.ascii_letters)

    letter_to_be_replaced = random.choice(input_string)
    letter_to_replace_with = generateRandomLetter()

    new_string = input_string.replace(letter_to_be_replaced, letter_to_replace_with)
    return new_string
