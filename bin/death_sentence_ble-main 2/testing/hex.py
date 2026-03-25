import asyncio
from bleak import BleakClient
import crcmod
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

# Test sequences
sequences = [
    (1, 5),
    (2, 5),
    (3, 5),
    (1, 10)
]

print("Generated commands for the test sequence:")
print("=" * 50)

for scent_id, duration in sequences:
    cmd = build_command(scent_id, duration)
    print(f"Scent {scent_id}, {duration}s → {cmd.hex().upper()}")

print("\nVerification against provided examples:")
print("-" * 40)

# Verify against your examples
cmd1 = build_command(1, 5)
expected1 = "F500000001020501000013882BD455"
print(f"Scent 1, 5s: {cmd1.hex().upper()}")
print(f"Expected:    {expected1}")
print(f"Match: {'✓' if cmd1.hex().upper() == expected1 else '✗'}")

cmd2 = build_command(2, 5)
expected2 = "F500000001020502000013882B9055"
print(f"\nScent 2, 5s: {cmd2.hex().upper()}")
print(f"Expected:    {expected2}")
print(f"Match: {'✓' if cmd2.hex().upper() == expected2 else '✗'}")

cmd2 = build_command(3, 5)
expected2 = "F500000001020502000013882B9055"
print(f"\nScent 2, 5s: {cmd2.hex().upper()}")
print(f"Expected:    {expected2}")
print(f"Match: {'✓' if cmd2.hex().upper() == expected2 else '✗'}")

cmd2 = build_command(1, 10)
expected2 = "F500000001020502000013882B9055"
print(f"\nScent 2, 5s: {cmd2.hex().upper()}")
print(f"Expected:    {expected2}")
print(f"Match: {'✓' if cmd2.hex().upper() == expected2 else '✗'}")

