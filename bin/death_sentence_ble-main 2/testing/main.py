import asyncio
from bleak import BleakClient
import crcmod

BLE_ADDRESS = "F7C9C411-AEA2-2415-8BC2-2A56B42DC7F8"  # wear_08f9e0dfb9a6
WRITE_CHAR_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"

def crc16_modbus(data: bytes) -> bytes:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    # Return in big-endian format to match the examples
    return bytes([(crc >> 8) & 0xFF, crc & 0xFF])

def build_command(scent: int, duration_sec: int) -> bytes:
    start = bytes([0xF5])
    header = bytes([0x00, 0x00, 0x00, 0x01])
    cmd_type = bytes([0x02])
    subcmd = bytes([0x05])
    channel = bytes([scent])
    padding = bytes([0x00, 0x00])
    
    # Duration in milliseconds, but only use 2 bytes (big-endian)
    duration_ms = duration_sec * 1000
    duration_bytes = duration_ms.to_bytes(2, 'big')  # Only 2 bytes

    body = header + cmd_type + subcmd + channel + padding + duration_bytes
    crc_bytes = crc16_modbus(body)
    end = bytes([0x55])

    return start + body + crc_bytes + end

async def play_sequence(sequence):
    async with BleakClient(BLE_ADDRESS) as client:
        print(f"Connecting to {BLE_ADDRESS}...")
        await client.connect()

        if not client.is_connected:
            print("Failed to connect!")
            return
        print("Connected!")

        for scent_id, duration in sequence:
            cmd = build_command(scent_id, duration)
            print(f"Sending scent {scent_id} for {duration}s → {cmd.hex().upper()}")
            await client.write_gatt_char(WRITE_CHAR_UUID, cmd)
            await asyncio.sleep(duration)

if __name__ == "__main__":
    sequence = [
        (4, 5),
        (11, 3),
        (7, 8),
        (5, 2)
    ]
    for scent, duration in sequence:
        res = build_command(scent,duration).hex()
        print(res)
    # asyncio.run(play_sequence(sequence))

