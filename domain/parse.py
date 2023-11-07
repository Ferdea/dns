from io import BytesIO
from domain.models import Message, Header, Question, Answer


def _parse_header(data: BytesIO) -> Header:
    transaction_id: int = int.from_bytes(data.read(2), byteorder='big')
    flags: bytes = data.read(2)
    qd_count: int = int.from_bytes(data.read(2), byteorder='big')
    an_count: int = int.from_bytes(data.read(2), byteorder='big')
    ns_count: int = int.from_bytes(data.read(2), byteorder='big')
    ar_count: int = int.from_bytes(data.read(2), byteorder='big')
    return Header(transaction_id, flags, qd_count, an_count, ns_count, ar_count)


def _parse_name(data: BytesIO) -> list[bytes]:
    name: list[bytes] = []
    while True:
        part_length = int.from_bytes(data.read(2))
        if part_length == 0:
            break
        if part_length < 64:
            name.append(data.read(part_length))
        else:
            pass
    raise NotImplemented
    return name


def _parse_question(data: BytesIO) -> Question:
    raise NotImplemented


def parse_message(message: bytes) -> Message:
    data: BytesIO = BytesIO(message)
    header: Header = _parse_header(data)

    raise NotImplemented
