from asyncio import run
from domain.dns import start_dns


async def main():
    IP = '127.0.0.1'
    PORT = 53
    await start_dns(IP, PORT)


run(main())
