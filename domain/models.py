from dataclasses import dataclass


@dataclass
class Header:
    transaction_id: int
    flags: bytes
    qd_count: int
    an_count: int
    ns_count: int
    ar_count: int


@dataclass
class Question:
    q_name: list[str]
    q_type: int
    q_class: int


@dataclass
class Answer:
    a_name: list[str]
    a_type: int
    a_class: int
    ttl: int
    rd_length: int
    rdata: bytes | list[bytes]


@dataclass
class Message:
    header: Header
    question: list[Question]
    answer: list[Answer]
    authority: list[Answer]
    additional: list[Answer]
