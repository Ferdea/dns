from socket import socket, AF_INET, SOCK_DGRAM
from multiprocessing import Process
from logging import info
from domain.models import Message, Question
from domain.parse import parse_message
from domain.request import create_request
from domain.response import create_response


class DnsServer:
    def __init__(self, host: str, port: int):
        self.host: str = host
        self.port: int = port
        self.socket = socket(AF_INET, SOCK_DGRAM)

    def start_server(self):
        info('Dns server is starting...')
        self.socket.bind((self.host, self.port))
        while True:
            data, address = self.socket.recvfrom(4096)
            process = Process(
                target=self.handle_connection,
                args=(data, address)
            )
            process.start()

    def handle_connection(self, data: bytes, address: str) -> None:
        info(f'Handle connection from {address} with data: {data}')
        message: Message = parse_message(data)
        answer: bytes = self.find_ip(
            message.question[0].q_name,
            message.header.transaction_id
        )
        self.socket.sendto(answer, address)

    def find_ip(self, name: list[str], transaction_id: int) -> bytes:
        ips = ['192.203.230.10']
        dns_server_socket = socket(AF_INET, SOCK_DGRAM)

        while ips:
            ip = ips.pop()
            info(f'Pop ip: {ip}')
            request = create_request('.'.join(name), transaction_id)
            dns_server_socket.sendto(request, (ip, 53))
            info(f'Send request to dns server with ip: {ip}')

            response, address = dns_server_socket.recvfrom(4096)
            info(f'Get response from dns server {address} with data: {response}')
            message = parse_message(response)

            for answer in message.answer:
                if answer.a_type == 1:
                    return response

            for additional in message.additional:
                if additional.a_type == 1:
                    ips.append('.'.join(list(str(part) for part in bytearray(additional.rdata))))

            if not any(additional.a_type == 1 for additional in message.additional):
                for authority in message.authority:
                    if authority.a_type == 2:
                        ips.append('.'.join(list(part.decode('utf-8') for part in authority.rdata)))
