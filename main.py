from socket import socket, AF_INET, SOCK_DGRAM
from utils import from_int_to_hex, from_hex_to_bytes
from domain.models import get_request, get_response


IP = '127.0.0.1'
PORT = 53

sock = socket(AF_INET, SOCK_DGRAM)
sock.bind((IP, PORT))
data, address = sock.recvfrom(4096)
header, request = get_request(data)
print(header, request)
print(request.get_requested_address())

sock2 = socket(AF_INET, SOCK_DGRAM)
sock2.sendto(data, ('8.8.8.8', 53))
data2, address2 = sock2.recvfrom(4096)
header, request, response = get_response(data2)
print(header, request, response)
print(request.get_requested_address(), response.get_ip())

if request.get_requested_address() == 'alexbers.com':
    response.rdlength = from_int_to_hex(8)
    response.rdata = ''.join(from_int_to_hex(228) for _ in range(4))
    data2 = from_hex_to_bytes(header.to_str() + request.to_str() + response.to_str())

sock.sendto(data2, address)
