import base64


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


def checkResponseDataStructureForDelegationContractAddress(data: str) -> bool:
    if "@6f6b@" in data:
        data = data.split("@6f6b@")
        if "'" in data[1]:
            data = data[1].replace("'", "")
            if len(data) == 64:
                return True
    else:
        return False
