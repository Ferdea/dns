from struct import pack


def create_request(
        name: str,
        transaction_id: int,
        flags: bytes = b'\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00'
) -> bytes:
    request: bytes = pack('!H', transaction_id) + flags

    for part in name.split('.'):
        encoded_part = part.encode()
        request += pack('!B', len(encoded_part)) + encoded_part

    request += pack('!B2H', 0, 1, 1)
    return request
