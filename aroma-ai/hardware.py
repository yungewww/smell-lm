import asyncio
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from bleak import BleakClient, BleakScanner

app = Flask(__name__)
CORS(app)

# ─── Config ───────────────────────────────────────────────────────────────────

DEVICE_NAME_KEYWORD = "wear"
WRITE_CHAR_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"

_cached_device_address = None

# ─── BLE Helpers ──────────────────────────────────────────────────────────────

async def find_device(timeout: float = 10.0) -> str | None:
    global _cached_device_address

    if _cached_device_address:
        try:
            async with BleakClient(_cached_device_address, timeout=5.0) as client:
                if client.is_connected:
                    return _cached_device_address
        except Exception:
            _cached_device_address = None

    devices = await BleakScanner.discover(timeout=timeout)
    for device in devices:
        if device.name and DEVICE_NAME_KEYWORD.lower() in device.name.lower():
            _cached_device_address = device.address
            return device.address

    return None


def crc16_modbus(data: bytes) -> bytes:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return bytes([(crc >> 8) & 0xFF, crc & 0xFF])


def build_command(scent_id: int, duration_sec: int) -> bytes:
    header   = bytes([0x00, 0x00, 0x00, 0x01])
    cmd_type = bytes([0x02])
    subcmd   = bytes([0x05])
    channel  = bytes([scent_id])
    padding  = bytes([0x00, 0x00])
    duration_bytes = (duration_sec * 1000).to_bytes(2, 'big')

    body = header + cmd_type + subcmd + channel + padding + duration_bytes
    crc  = crc16_modbus(body)

    return bytes([0xF5]) + body + crc + bytes([0x55])

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/play_sequence")
def play_sequence():
    data     = request.get_json()
    sequence = data.get("sequence", [])

    if not sequence:
        return jsonify({"status": "error", "message": "No sequence provided"}), 400

    for i, item in enumerate(sequence):
        scent_id = item.get("scent_id")
        duration = item.get("scent_duration", item.get("duration", 5))

        if not isinstance(scent_id, int) or not (1 <= scent_id <= 12):
            return jsonify({"status": "error", "message": f"Invalid scent_id in item {i}"}), 400
        if not isinstance(duration, (int, float)) or not (1 <= duration <= 60):
            return jsonify({"status": "error", "message": f"Invalid duration in item {i}"}), 400

    result = asyncio.run(_play_sequence(sequence))
    return jsonify(result)


@app.post("/play_scent")
def play_scent():
    data     = request.get_json()
    scent_id = data.get("scent_id", 1)
    duration = data.get("scent_duration", data.get("duration", 5))

    if not isinstance(scent_id, int) or not (1 <= scent_id <= 12):
        return jsonify({"status": "error", "message": "Invalid scent_id. Must be 1–12"}), 400
    if not isinstance(duration, (int, float)) or not (1 <= duration <= 60):
        return jsonify({"status": "error", "message": "Invalid duration. Must be 1–60"}), 400

    result = asyncio.run(_play_single(scent_id, int(duration)))
    return jsonify(result)


@app.get("/test_connection")
def test_connection():
    result = asyncio.run(_test_connection())
    return jsonify(result)

# ─── Async BLE Logic ──────────────────────────────────────────────────────────

async def _play_sequence(sequence: list) -> dict:
    address = await find_device()
    if not address:
        return {"status": "error", "message": f"Device '{DEVICE_NAME_KEYWORD}' not found"}

    try:
        async with BleakClient(address) as client:
            for item in sequence:
                scent_id = item["scent_id"]
                duration = int(item.get("scent_duration", item.get("duration", 5)))
                cmd = build_command(scent_id, duration)
                await client.write_gatt_char(WRITE_CHAR_UUID, cmd)
                print(f"Sent scent {scent_id} for {duration}s → {cmd.hex().upper()}")
                await asyncio.sleep(duration)
        return {"status": "success", "message": "Sequence completed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def _play_single(scent_id: int, duration: int) -> dict:
    address = await find_device()
    if not address:
        return {"status": "error", "message": f"Device '{DEVICE_NAME_KEYWORD}' not found"}

    try:
        async with BleakClient(address) as client:
            cmd = build_command(scent_id, duration)
            await client.write_gatt_char(WRITE_CHAR_UUID, cmd)
            print(f"Sent scent {scent_id} for {duration}s → {cmd.hex().upper()}")
        return {"status": "success", "message": f"Scent {scent_id} sent for {duration}s"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def _test_connection() -> dict:
    address = await find_device()
    if not address:
        return {"status": "error", "message": f"Device '{DEVICE_NAME_KEYWORD}' not found"}

    try:
        async with BleakClient(address, timeout=10.0) as client:
            if client.is_connected:
                return {"status": "success", "message": "Connected", "address": address}
            return {"status": "error", "message": "Failed to connect"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Hardware server starting on port 5001")
    print(f"Looking for BLE device with '{DEVICE_NAME_KEYWORD}' in name")
    app.run(host="0.0.0.0", port=5001, debug=True)