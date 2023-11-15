from io import BytesIO
from domain.models import Message, Header, Question, Answer
from logging import info


class MessageParser:
    def parse_message(self, message: bytes) -> Message:
        data: BytesIO = BytesIO(message)
        header: Header = self._parse_header(data)

        questions: list[Question] = \
            [self._parse_question(data) for _ in range(header.qd_count)]
        answers: list[Answer] = \
            [self._parse_answer(data) for _ in range(header.an_count)]
        authority: list[Answer] = \
            [self._parse_answer(data) for _ in range(header.ns_count)]
        additional: list[Answer] = \
            [self._parse_answer(data) for _ in range(header.ar_count)]

        return Message(header, questions, answers, authority, additional)

    def _parse_header(self, data: BytesIO) -> Header:
        transaction_id: int = int.from_bytes(data.read(2), byteorder='big')
        flags: bytes = data.read(2)
        qd_count: int = int.from_bytes(data.read(2), byteorder='big')
        an_count: int = int.from_bytes(data.read(2), byteorder='big')
        ns_count: int = int.from_bytes(data.read(2), byteorder='big')
        ar_count: int = int.from_bytes(data.read(2), byteorder='big')
        info(f'Parsed header with transaction id: {transaction_id}')
        return Header(transaction_id, flags, qd_count, an_count, ns_count, ar_count)

    def _parse_name(self, data: BytesIO) -> list[bytes]:
        name: list[bytes] = []
        while True:
            q = data.read(1)
            part_length = int.from_bytes(q, byteorder='big')

            if part_length == 0:
                break

            if part_length < 64:
                name.append(data.read(part_length))
            else:
                jump_index = part_length % 64 + int.from_bytes(data.read(1), byteorder='big')
                saved_index = data.tell()
                data.seek(jump_index)
                name = self._parse_name(data)
                data.seek(saved_index)
                return name

        return name

    def _parse_question(self, data: BytesIO) -> Question:
        q_name: list[str] = [part.decode() for part in self._parse_name(data)]
        q_type: int = int.from_bytes(data.read(2), byteorder='big')
        q_class: int = int.from_bytes(data.read(2), byteorder='big')
        return Question(q_name, q_type, q_class)

    def _parse_answer(self, data: BytesIO) -> Answer:
        a_name: list[str] = [part.decode() for part in self._parse_name(data)]
        a_type: int = int.from_bytes(data.read(2), byteorder='big')
        a_class: int = int.from_bytes(data.read(2), byteorder='big')
        ttl: int = int.from_bytes(data.read(4), byteorder='big')
        rd_length: int = int.from_bytes(data.read(2), byteorder='big')
        rdata: bytes | list[bytes] = self._parse_name(data) \
            if a_type == 2 else data.read(rd_length)
        return Answer(a_name, a_type, a_class, ttl, rd_length, rdata)


def parse_message(message: bytes) -> Message:
    return MessageParser().parse_message(message)
