#This is a sample Python script.

import binascii
import sys

from ScentRealmForNeckWear.ScentRealmProtocol import NeckWear
import serial.tools.list_ports
import random
import time
import serial
from bleak import BleakScanner, BleakClient
import asyncio

async def scan():
    devices = await BleakScanner.discover()
    for d in devices:
        print(f"Name: {d.name}, Address: {d.address}")
        
asyncio.run(scan())

# address = Name: wear_08f9e0dfb9a6, Address: FC28F7A3-F547-7342-1F57-BB2939694BDC

address = "FC28F7A3-F547-7342-1F57-BB2939694BDC"

# async def explore_services(address):
#     async with BleakClient(address) as client:
#         await client.connect()
#         services = client.services  # now a BleakGATTServiceCollection
#         for service in services:
#             print(f"Service: {service.uuid}")
#             for char in service.characteristics:
#                 props = ",".join(char.properties)
#                 print(f"Characteristic: {char.uuid} [{props}]")
                
# asyncio.run(explore_services(address))

