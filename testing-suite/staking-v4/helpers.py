import base64
from constants import *

def stringToHex(value):
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


