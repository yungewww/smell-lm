# DeathScent BLE - Changelog

## [Dynamic Device Discovery Update] - 2025-10-20

### ✨ New Features

#### 🔍 Automatic Device Discovery
- **No more hardcoded addresses!** The system now automatically finds your device by name
- Searches for any device containing "wear" in its name
- Eliminates the need to manually update device addresses

#### 💾 Smart Caching
- Device address is cached after first connection
- Faster reconnections using cached address
- Automatically rescans if cached device is unavailable

#### 🔄 Self-Healing Connections
- If the device disconnects or address changes, system automatically rescans
- Robust error handling with helpful messages
- Works seamlessly even if device is restarted

### 🔧 Technical Changes

#### Modified Files:
1. **backend.py**
   - Added `find_device_by_name()` function for dynamic discovery
   - Changed from hardcoded `BLE_ADDRESS` to `DEVICE_NAME_KEYWORD = "wear"`
   - Updated all connection functions to use dynamic discovery:
     - `play_scent_ble()`
     - `play_sequence_ble()`
     - `test_ble_connection()`
   - Added device address caching for performance
   - Improved error messages with device name information

2. **readme.md**
   - Added "How Device Discovery Works" section
   - Updated troubleshooting guide
   - Simplified setup instructions

3. **testing/main.py**
   - Updated device address to match current device

4. **scan_devices.py**
   - Improved output formatting
   - Added device name filtering
   - Better error messages for macOS permissions

### 📋 Configuration

#### Customizing Device Search
To search for devices with a different keyword, edit `backend.py` line 9:
```python
DEVICE_NAME_KEYWORD = "your-keyword"  # Default is "wear"
```

### 🎯 Benefits

1. **Portable**: Code works across different devices without modification
2. **User-Friendly**: No need to run scanner and manually update addresses
3. **Reliable**: Automatically handles device address changes
4. **Fast**: Caching ensures quick reconnections
5. **Scalable**: Easy to support multiple devices with different keywords

### 🔄 Migration from Hardcoded Addresses

**Before:**
```python
BLE_ADDRESS = "FC28F7A3-F547-7342-1F57-BB2939694BDC"  # Fixed address
```

**After:**
```python
DEVICE_NAME_KEYWORD = "wear"  # Search by name, address found automatically
```

### 🚀 Usage

No changes needed! Just:
1. Make sure your device name contains "wear"
2. Start the server: `python run.py`
3. The device will be automatically discovered on first connection

### ⚠️ Requirements

- Device name **must contain** the keyword (default: "wear")
- Device must be powered on and in Bluetooth range
- Bluetooth permissions enabled on your system

