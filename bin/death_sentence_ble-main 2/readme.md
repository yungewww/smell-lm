# Death Sentence BLE - AI-Powered Scent Sequencer 🌹💀

An integrated system combining AI-generated scent sequences with BLE device control. Generate death-themed fragrance compositions using OpenAI, then play them on your physical scent device.

## 🚀 Quick Start

**Prerequisites:**
- Python 3.9+
- OpenAI API key
- BLE scent device with "wear" in its name

**Three Simple Steps:**

### 1. Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd death_sentence/agents
pip install -r requirements.txt
cd ../..
```

### 2. Set OpenAI API Key
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. Start All Services

**🚀 EASY WAY - Single Command (Recommended):**
```bash
export OPENAI_API_KEY="your-key-here"
./start_all.sh
```
This automatically opens 3 Terminal tabs with all services!

**📋 MANUAL WAY - 3 Separate Terminals:**

**Terminal 1 - BLE Backend:**
```bash
./start_ble_backend.sh
# Or manually: python backend.py
```

**Terminal 2 - AI Backend:**
```bash
./restart_ai_backend.sh
# Or manually: cd death_sentence/agents && uvicorn app:app --reload --port 8000
```

**Terminal 3 - Frontend:**
```bash
./start_frontend.sh
# Or manually: cd death_sentence && python3 -m http.server 8080
```

### 4. Use the App
1. Open http://localhost:8080 in your browser
2. Enter a death-themed sentence (e.g., "I want to die in the forest alone..")
3. Click "SYNTHIZE SCENT →"
4. Click "TEST DEVICE CONNECTION" to verify BLE device
5. Click "▶ PLAY SEQUENCE ON DEVICE" to play!

## 📖 Full Documentation

See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for complete setup, API documentation, and troubleshooting.

## How Device Discovery Works

The system **automatically finds your device** by searching for BLE devices with **"wear"** in the name.

### Features:
- ✅ **No hardcoded addresses** - device is discovered dynamically
- ✅ **Automatic caching** - once found, the address is cached for faster reconnection
- ✅ **Self-healing** - if cached device disconnects, it will scan again
- ✅ **Multiple device support** - finds any device with "wear" in the name

### Device Requirements:
Your device name **must contain "wear"** (case-insensitive). Examples:
- `wear_08f9e0dfb9a6` ✅
- `MyWearableDevice` ✅
- `WEAR-Scent-01` ✅

---

## Troubleshooting Device Connection

If you get "Device not found" errors:

### Step 1: Make sure your device is ready
- ✅ Device is **powered ON**
- ✅ Device is within **Bluetooth range** (2-10 meters)
- ✅ Device is **not connected** to another device/app
- ✅ Bluetooth is **enabled** on your computer
- ✅ Device name contains **"wear"**

### Step 2: Test the connection
1. Run `python run.py`
2. Open http://localhost:5001
3. Click **"🔍 Test Device Connection"** button
4. It will show the device name and address if found

### Step 3: Scan for available devices (Optional)
If the device is not found, scan for all nearby BLE devices:
```bash
python scan_devices.py
```
This will show all devices with names. Look for your device in the list.

### Step 4: Change the search keyword (if needed)
If your device doesn't have "wear" in its name, edit `backend.py` line 9:
```python
DEVICE_NAME_KEYWORD = "your-keyword-here"  # Change "wear" to match your device name
```

Then restart the server:
```bash
python run.py
```