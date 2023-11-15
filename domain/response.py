from struct import pack
from domain.request import create_request


def create_response(
        name: str,
        transaction_id: int,
        ip: str
) -> bytes:
    response: bytes = create_request(name, transaction_id, b'\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00')

    for part in name.split('.'):
        encoded_part = part.encode()
        response += pack('!B', len(encoded_part)) + encoded_part

    ip_data = pack('!4B', *[int(part) for part in ip.split('.')])

    response += pack('!B2HIH', 0, 1, 1, 60, len(ip_data)) + ip_data
    return response
