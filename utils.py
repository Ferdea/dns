from binascii import hexlify, unhexlify


def from_bytes_to_hex(input_bytes: bytes) -> str:
    return hexlify(input_bytes).decode('utf-8')


def from_hex_to_bytes(input_hex: str) -> bytes:
    return unhexlify(input_hex.encode('utf-8'))


def from_hex_to_int(input_hex: str) -> int:
    return int(input_hex, 16)


def from_int_to_hex(input_int: int) -> str:
    return hex(input_int)[2:]


def from_hex_to_binary(input_hex: str) -> str:
    return bin(from_hex_to_int(input_hex))[2:].zfill(4 * len(input_hex))


def from_binary_to_hex(input_binary: str) -> str:
    return hex(int(input_binary, 2))[2:]
