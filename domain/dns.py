from logging import info, basicConfig, INFO
from sys import stdout
from asyncio import Server, DatagramProtocol, DatagramTransport, get_running_loop, Future, AbstractEventLoop, Task, run_coroutine_threadsafe
from concurrent.futures import wait, ALL_COMPLETED, as_completed
from domain.models import Message, Question
from domain.parse import parse_message
from domain.request import create_request
from domain.response import create_response


class DnsServerProtocol(DatagramProtocol):
    def __init__(self, loop: AbstractEventLoop):
        super().__init__()
        self.on_connection_lost = loop.create_future()
        self.transport = None

    def connection_made(self, transport: DatagramTransport) -> None:
        self.transport: DatagramTransport = transport

    def datagram_received(self, data: bytes, address: str) -> None:
        message: Message = parse_message(data)
        info(f'Handle connection from {address} to get: {".".join(message.question[0].q_name)}')

        if 'multiply' in message.question[0].q_name:
            answer: bytes = (
                DnsServer.handle_multiply_request('.'.join(message.question[0].q_name), message.header.transaction_id))
        else:
            loop: AbstractEventLoop = get_running_loop()
            for f in as_completed([run_coroutine_threadsafe(
                    DnsServer.find_ip(message.question[0].q_name, message.header.transaction_id), loop=loop)], None):
                answer: bytes = f.result(None)

        self.transport.sendto(answer, address)

    def connection_lost(self, exception: Exception) -> None:
        self.on_connection_lost.set_result(True)


class DnsClientProtocol(DatagramProtocol):
    def __init__(self, message: bytes, loop: AbstractEventLoop):
        super().__init__()
        self.message = message
        self.on_connection_lost: Future = loop.create_future()
        self.transport: DatagramTransport | None = None
        self.data: bytes | None = None

    def connection_made(self, transport: DatagramTransport) -> None:
        self.transport: DatagramTransport = transport
        self.transport.sendto(self.message)

    def datagram_received(self, data: bytes, address: str) -> None:
        info(f'Received data from address: {address}')
        self.data = data
        self.transport.close()

    def connection_lost(self, exception: Exception) -> None:
        self.on_connection_lost.set_result(True)


class DnsServer:
    def __init__(self, host: str, port: int):
        self.host: str = host
        self.port: int = port
        self.server: Server | None = None

    async def start_server(self) -> None:
        loop = get_running_loop()

        info('Dns server is starting...')
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: DnsServerProtocol(loop),
            local_addr=(self.host, self.port))

        try:
            await protocol.on_connection_lost
        finally:
            transport.close()

    @staticmethod
    async def find_ip(name: list[str], transaction_id: int) -> bytes:
        ips = ['192.203.230.10']

        loop = get_running_loop()

        while ips:
            ip = ips.pop()
            request = create_request('.'.join(name), transaction_id)

            transport, protocol = await loop.create_datagram_endpoint(
                lambda: DnsClientProtocol(request, loop),
                remote_addr=(ip, 53))

            try:
                await protocol.on_connection_lost
            finally:
                transport.close()

            response = protocol.data
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

    @staticmethod
    def handle_multiply_request(name: str, transaction_id: int) -> bytes:
        result = 1

        for number in name.split('.')[:-1]:
            result *= int(number) % 256

        return create_response(name, transaction_id, f'127.0.0.{result}')


async def start_dns(host: str, port: int) -> None:
    basicConfig(level=INFO, stream=stdout)
    dns_server = DnsServer(host, port)
    await dns_server.start_server()
