from socket import socket, AF_INET, SOCK_DGRAM
from domain.dns import DnsServer
from logging import basicConfig, INFO
from sys import stdout

IP = '127.0.0.1'
PORT = 53

basicConfig(level=INFO, stream=stdout)
dns = DnsServer(IP, PORT)
dns.start_server()
