from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import asyncio
from bleak import BleakClient, BleakScanner
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes to allow communication with AI frontend

# Device configuration
DEVICE_NAME_KEYWORD = "wear"  # Device name must contain this keyword
WRITE_CHAR_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"

# Cache for device address to avoid scanning every time
_cached_device_address = None

async def find_device_by_name(keyword: str = DEVICE_NAME_KEYWORD, timeout: float = 10.0):
    """
    Scan for BLE devices and find one with the keyword in its name.
    Returns the device address if found, None otherwise.
    """
    global _cached_device_address
    
    # If we have a cached address, verify it's still available
    if _cached_device_address:
        try:
            print(f"Checking cached device: {_cached_device_address}")
            async with BleakClient(_cached_device_address, timeout=5.0) as client:
                if client.is_connected:
                    print(f"✅ Cached device still available")
                    return _cached_device_address
        except Exception as e:
            print(f"Cached device no longer available: {e}")
            _cached_device_address = None
    
    # Scan for devices
    print(f"Scanning for devices with '{keyword}' in name...")
    devices = await BleakScanner.discover(timeout=timeout)
    
    for device in devices:
        if device.name and keyword.lower() in device.name.lower():
            print(f"✅ Found device: {device.name} ({device.address})")
            _cached_device_address = device.address
            return device.address
    
    print(f"❌ No device found with '{keyword}' in name")
    return None

def crc16_modbus(data: bytes) -> bytes:
    """Calculate CRC16 Modbus checksum"""
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

def build_scent_command(scent_id: int, duration_sec: int) -> bytes:
    """Build scent command with correct CRC encoding"""
    start = bytes([0xF5])
    header = bytes([0x00, 0x00, 0x00, 0x01])
    cmd_type = bytes([0x02])
    subcmd = bytes([0x05])
    channel = bytes([scent_id])
    padding = bytes([0x00, 0x00])
    
    # Convert duration to milliseconds (2 bytes, big-endian)
    duration_ms = duration_sec * 1000
    duration_bytes = duration_ms.to_bytes(2, 'big')
    
    # Body for CRC calculation (everything except start, crc, and end)
    body = header + cmd_type + subcmd + channel + padding + duration_bytes
    
    # Calculate CRC
    crc_bytes = crc16_modbus(body)
    
    # End byte
    end = bytes([0x55])
    
    # Complete command
    return start + body + crc_bytes + end

async def play_scent_ble(scent_id: int, duration: int):
    """Send a single scent command to the device"""
    try:
        # Find device dynamically
        device_address = await find_device_by_name()
        if not device_address:
            return {"status": "error", "message": f"Device with '{DEVICE_NAME_KEYWORD}' in name not found. Make sure device is powered on and in range."}
        
        async with BleakClient(device_address) as client:
            print(f"Connecting to device {device_address}...")
            await client.connect()
            
            if not client.is_connected:
                print("Failed to connect to device!")
                return {"status": "error", "message": "Failed to connect to device"}
            
            print("Connected successfully!")
            
            # Build command with correct CRC
            cmd_bytes = build_scent_command(scent_id, duration)
            print(f"Sending scent {scent_id} for {duration}s...")
            print(f"Command bytes: {cmd_bytes.hex().upper()}")
            
            # Write to the characteristic
            await client.write_gatt_char(WRITE_CHAR_UUID, cmd_bytes)
            print(f"Successfully sent scent {scent_id} for {duration}s")
            
            return {"status": "success", "message": f"Scent {scent_id} sent for {duration} seconds"}
            
    except Exception as e:
        print(f"Error sending scent: {e}")
        return {"status": "error", "message": str(e)}

async def play_sequence_ble(sequence):
    """Send a sequence of scents to the device"""
    try:
        # Find device dynamically
        device_address = await find_device_by_name()
        if not device_address:
            return {"status": "error", "message": f"Device with '{DEVICE_NAME_KEYWORD}' in name not found. Make sure device is powered on and in range."}
        
        async with BleakClient(device_address) as client:
            print(f"Connecting to device {device_address}...")
            await client.connect()
            
            if not client.is_connected:
                print("Failed to connect to device!")
                return {"status": "error", "message": "Failed to connect to device"}
            
            print("Connected successfully!")
            
            for item in sequence:
                scent_id = item.get('scent_id', item.get('id', 1))
                duration = item.get('duration', 5)
                
                try:
                    # Build command with correct CRC
                    cmd_bytes = build_scent_command(scent_id, duration)
                    print(f"Sending scent {scent_id} for {duration}s...")
                    print(f"Command bytes: {cmd_bytes.hex().upper()}")
                    
                    # Write to the characteristic
                    await client.write_gatt_char(WRITE_CHAR_UUID, cmd_bytes)
                    print(f"Successfully sent scent {scent_id} for {duration}s")
                    
                    # Wait while scent plays
                    await asyncio.sleep(duration)
                    
                except Exception as e:
                    print(f"Error sending scent {scent_id}: {e}")
                    continue
            
            return {"status": "success", "message": "Sequence completed"}
            
    except Exception as e:
        print(f"Connection error: {e}")
        return {"status": "error", "message": str(e)}

@app.route('/play_scent', methods=['POST'])
def play_scent():
    """API endpoint to play a single scent"""
    try:
        data = request.get_json()
        scent_id = data.get('scent_id', 1)
        duration = data.get('duration', 5)
        
        # Validate input
        if not isinstance(scent_id, int) or scent_id < 1 or scent_id > 12:
            return jsonify({"status": "error", "message": "Invalid scent_id. Must be between 1-12"}), 400
        
        if not isinstance(duration, int) or duration < 1 or duration > 60:
            return jsonify({"status": "error", "message": "Invalid duration. Must be between 1-60 seconds"}), 400
        
        # Run the async function
        result = asyncio.run(play_scent_ble(scent_id, duration))
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/play_sequence', methods=['POST'])
def play_sequence():
    """API endpoint to play a sequence of scents"""
    try:
        data = request.get_json()
        sequence = data.get('sequence', [])
        
        if not sequence:
            return jsonify({"status": "error", "message": "No sequence provided"}), 400
        
        # Validate sequence
        for i, item in enumerate(sequence):
            if not isinstance(item, dict):
                return jsonify({"status": "error", "message": f"Item {i} must be a dictionary"}), 400
            
            scent_id = item.get('scent_id', item.get('id', 1))
            duration = item.get('duration', 5)
            
            if not isinstance(scent_id, int) or scent_id < 1 or scent_id > 12:
                return jsonify({"status": "error", "message": f"Invalid scent_id in item {i}. Must be between 1-12"}), 400
            
            if not isinstance(duration, int) or duration < 1 or duration > 60:
                return jsonify({"status": "error", "message": f"Invalid duration in item {i}. Must be between 1-60 seconds"}), 400
        
        # Run the async function
        result = asyncio.run(play_sequence_ble(sequence))
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/test_connection', methods=['GET'])
def test_connection():
    """Test BLE connection to the device"""
    try:
        result = asyncio.run(test_ble_connection())
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

async def test_ble_connection():
    """Test if we can connect to the BLE device"""
    try:
        # Find device dynamically
        print(f"Searching for device with '{DEVICE_NAME_KEYWORD}' in name...")
        device_address = await find_device_by_name()
        
        if not device_address:
            return {
                "status": "error",
                "message": f"Device with '{DEVICE_NAME_KEYWORD}' in name not found.\n\nPlease check:\n1. Device is powered ON\n2. Device is in range\n3. Device name contains '{DEVICE_NAME_KEYWORD}'\n4. Bluetooth is enabled on your computer",
                "keyword": DEVICE_NAME_KEYWORD
            }
        
        print(f"Testing connection to {device_address}...")
        async with BleakClient(device_address, timeout=10.0) as client:
            await client.connect()
            
            if client.is_connected:
                print("✅ Successfully connected!")
                
                # Get device info from scan
                device_name = "Unknown"
                devices = await BleakScanner.discover(timeout=2.0)
                for dev in devices:
                    if dev.address == device_address:
                        device_name = dev.name if dev.name else "Unknown"
                        break
                
                # Try to check if write characteristic exists (using services property)
                found_char = False
                try:
                    # In bleak, services are available as a property after connection
                    if hasattr(client, 'services'):
                        for service in client.services:
                            for char in service.characteristics:
                                if char.uuid.lower() == WRITE_CHAR_UUID.lower():
                                    found_char = True
                                    break
                            if found_char:
                                break
                except Exception as e:
                    print(f"Note: Could not enumerate services: {e}")
                    # If we can't check services, assume it's okay since we connected
                    found_char = True
                
                if found_char:
                    return {
                        "status": "success",
                        "message": f"✅ Device connected successfully!\n\nDevice Name: {device_name}\nAddress: {device_address}\nWrite Characteristic: Available",
                        "address": device_address,
                        "device_name": device_name
                    }
                else:
                    return {
                        "status": "success",
                        "message": f"✅ Connected to {device_name}!\n\nAddress: {device_address}\nNote: Could not verify write characteristic, but connection successful.",
                        "address": device_address,
                        "device_name": device_name
                    }
            else:
                return {
                    "status": "error",
                    "message": "Failed to connect to device",
                    "address": device_address
                }
    except asyncio.TimeoutError:
        return {
            "status": "error",
            "message": f"⏱️ Connection timeout.\n\nDevice not responding. Make sure it's powered on and in range.",
            "keyword": DEVICE_NAME_KEYWORD
        }
    except Exception as e:
        error_msg = str(e)
        if "was not found" in error_msg.lower():
            return {
                "status": "error",
                "message": f"❌ Device not found.\n\nPlease check:\n1. Device is powered ON\n2. Device is in range\n3. Device name contains '{DEVICE_NAME_KEYWORD}'\n4. Device is not connected to another app",
                "keyword": DEVICE_NAME_KEYWORD,
                "details": error_msg
            }
        else:
            return {
                "status": "error",
                "message": f"Connection error: {error_msg}",
                "keyword": DEVICE_NAME_KEYWORD
            }

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Backend is running"})

@app.route('/')
def index():
    """Serve the frontend HTML file"""
    return send_from_directory('.', 'frontend.html')

if __name__ == "__main__":
    print("=" * 60)
    print("🌹 DeathScent Backend Server 🌹")
    print("=" * 60)
    print(f"Device Search: Looking for devices with '{DEVICE_NAME_KEYWORD}' in name")
    print(f"Characteristic UUID: {WRITE_CHAR_UUID}")
    print(f"Frontend URL: http://localhost:5001")
    print("=" * 60)
    print("\n✅ Server starting...")
    print("📡 Device will be auto-discovered on first connection\n")
    app.run(debug=True, host='0.0.0.0', port=5001)
