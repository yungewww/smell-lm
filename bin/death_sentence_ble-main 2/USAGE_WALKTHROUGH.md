# Death Sentence BLE - Visual Walkthrough

## 🎬 Step-by-Step Usage Guide

### Setup Phase (One-Time Setup)

#### Step 1: Install Dependencies
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install main dependencies
pip install -r requirements.txt

# Install AI dependencies
cd death_sentence/agents
pip install -r requirements.txt
cd ../..
```

#### Step 2: Set API Key
```bash
# Option 1: Export in terminal (temporary)
export OPENAI_API_KEY="sk-..."

# Option 2: Add to ~/.zshrc or ~/.bashrc (permanent)
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.zshrc
source ~/.zshrc
```

---

## 🚀 Running the System

### Step 3: Start Three Servers

Open **THREE** terminal windows:

#### Terminal 1: BLE Backend 🔵
```bash
cd /Users/awwu/Downloads/death_sentence_ble
./start_ble_backend.sh
```

**Expected Output:**
```
========================================
🌹 DeathScent Backend Server 🌹
========================================
Device Search: Looking for devices with 'wear' in name
Characteristic UUID: 6e400002-b5a3-f393-e0a9-e50e24dcca9e
Frontend URL: http://localhost:5001
========================================

✅ Server starting...
📡 Device will be auto-discovered on first connection

 * Running on http://0.0.0.0:5001
```

#### Terminal 2: AI Backend 🟢
```bash
cd /Users/awwu/Downloads/death_sentence_ble
./start_ai_backend.sh
```

**Expected Output:**
```
========================================
  Death Sentence AI Backend
========================================

📦 Activating virtual environment...
📦 Installing AI backend dependencies...

✅ Starting AI Backend on port 8000...
   Frontend: http://localhost:8080
   API: http://localhost:8000

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

#### Terminal 3: Frontend Server 🟡
```bash
cd /Users/awwu/Downloads/death_sentence_ble
./start_frontend.sh
```

**Expected Output:**
```
========================================
  Death Sentence Frontend
========================================

✅ Starting frontend server on port 8080...

🌐 Open in browser: http://localhost:8080

Serving HTTP on :: port 8080 (http://[::]:8080/) ...
```

---

## 💻 Using the Web Interface

### Step 4: Open Browser

Navigate to: **http://localhost:8080**

You'll see the **Death Sentence Fragrance Synthesizer** interface:

```
╔════════════════════════════════════════════════════════╗
║                 DEATH SCENTENCE                        ║
║           FRAGRANCE SYNTHESIZER                        ║
╠════════════════════════════════════════════════════════╣
║                                                        ║
║  ┌─────────────────────────────────────────┐ ┌────┐  ║
║  │ I want to die in the forest alone..     │ │ 🍃 │  ║
║  └─────────────────────────────────────────┘ └────┘  ║
║                                                        ║
║          [ SYNTHIZE SCENT → ]                         ║
║                                                        ║
╚════════════════════════════════════════════════════════╝
```

### Step 5: Generate Scent Sequence

1. **Enter Your Death Sentence**
   - Type a death-themed sentence
   - Examples:
     - "I want to die in the forest alone.."
     - "Lay me by the ocean during a storm.."
     - "Burn with the last library on earth.."
   
   💡 **Tip**: Click the 🍃 button for random suggestions!

2. **Click "SYNTHIZE SCENT →"**
   
   You'll see a loading animation with a spinning poison flask:
   ```
   ╔════════════════════════════════════╗
   ║         🧪 (spinning)              ║
   ║  Generating your death scentence...║
   ╚════════════════════════════════════╝
   ```

3. **View Generated Profile**
   
   After ~5-10 seconds, you'll see:
   ```
   ╔════════════════════════════════════════════════════════╗
   ║  GENERATED FRAGRANCE PROFILE:                          ║
   ╠════════════════════════════════════════════════════════╣
   ║  1. Grease (15s) [1]        ████████░░░░ 50%          ║
   ║  2. Smudge Stick (20s) [10] ████████████ 67%          ║
   ║  3. Coffin (10s) [2]        ████░░░░░░░░ 33%          ║
   ║  4. Mourning Wreath (15s) [5] ████████░░░░ 50%        ║
   ╠════════════════════════════════════════════════════════╣
   ║                  ╱ (needle)                            ║
   ║      ───────────●───────────                           ║
   ║   MORTALITY RATING: 7.2/10                             ║
   ╠════════════════════════════════════════════════════════╣
   ║  [ 🔍 TEST DEVICE CONNECTION ]                         ║
   ║  [ ▶ PLAY SEQUENCE ON DEVICE ]                         ║
   ╚════════════════════════════════════════════════════════╝
   ```

---

## 🎮 Device Control

### Step 6: Test Connection (Recommended First Time)

1. **Click "🔍 TEST DEVICE CONNECTION"**

2. **Possible Outcomes:**

   ✅ **Success:**
   ```
   ✅ Device connected successfully!
   
   Device Name: wear_08f9e0dfb9a6
   Address: 12:34:56:78:9A:BC
   Write Characteristic: Available
   ```

   ❌ **Device Not Found:**
   ```
   ❌ Device not found.
   
   Please check:
   1. Device is powered ON
   2. Device is in range
   3. Device name contains 'wear'
   4. Device is not connected to another app
   ```

   **Troubleshooting:**
   - Turn device OFF and ON again
   - Move device closer (within 2-3 meters)
   - Check device name with: `python scan_devices.py`
   - Ensure device isn't connected to phone/other computer

### Step 7: Play Sequence on Device 🎵

1. **Make Sure Device is Ready:**
   - ✅ Device powered ON
   - ✅ Device in range
   - ✅ Test connection passed (optional but recommended)

2. **Click "▶ PLAY SEQUENCE ON DEVICE"**

3. **What Happens:**
   ```
   Loading: "🔍 Finding device and starting sequence..."
   
   Backend Terminal Output:
   ────────────────────────────────────────
   Scanning for devices with 'wear' in name...
   ✅ Found device: wear_08f9e0dfb9a6 (12:34:56:78:9A:BC)
   Connecting to device 12:34:56:78:9A:BC...
   Connected successfully!
   Sending scent 1 for 15s...
   Command bytes: F500000001020501000000000F...
   Successfully sent scent 1 for 15s
   [waits 15 seconds]
   Sending scent 10 for 20s...
   Successfully sent scent 10 for 20s
   [waits 20 seconds]
   ...
   Sequence completed
   ────────────────────────────────────────
   
   Browser Alert:
   ✅ Sequence is playing on your device!
   ```

4. **Physical Device:**
   - Each scent plays in order
   - Duration matches AI-generated times
   - Total sequence ~60 seconds

---

## 🎯 Complete Example Session

### Example Input
```
"I want to disappear into the ancient forest, 
becoming one with moss and decay"
```

### AI Generated Sequence
```json
{
  "scent_sequence": [
    {"scent_name": "Grease", "scent_duration": 18},
    {"scent_name": "Smudge Stick", "scent_duration": 15},
    {"scent_name": "Grave Soil", "scent_duration": 12},
    {"scent_name": "Dead Body", "scent_duration": 15}
  ],
  "justification": "This composition evokes the slow decomposition 
  in a forest setting, with woody notes transitioning to earthen 
  decay and natural plant matter."
}
```

### Converted for BLE Device
```json
{
  "sequence": [
    {"scent_id": 1, "duration": 18},   // Grease (wood/forest)
    {"scent_id": 10, "duration": 15},  // Smudge Stick (eucalyptus/meditation)
    {"scent_id": 6, "duration": 12},   // Grave Soil (pollution/decay)
    {"scent_id": 9, "duration": 15}    // Dead Body (plant/earthy)
  ]
}
```

### Timeline
```
0s ───────── 18s ──────── 33s ──── 45s ──────── 60s
│    Grease   │  Smudge   │ Grave  │  Dead Body  │
│   (forest)  │  Stick    │ Soil   │   (decay)   │
└─────────────┴───────────┴────────┴─────────────┘
```

---

## 🔄 Workflow Diagram

```
┌─────────────────────────────────────────────────────────┐
│ USER ACTIONS                                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Type death sentence                                 │
│         ↓                                               │
│  2. Click "SYNTHIZE SCENT"                              │
│         ↓                                               │
│  3. Wait for AI (~5-10s)                                │
│         ↓                                               │
│  4. View generated profile                              │
│         ↓                                               │
│  5. Click "TEST CONNECTION" (optional)                  │
│         ↓                                               │
│  6. Click "PLAY SEQUENCE"                               │
│         ↓                                               │
│  7. Device plays scents!                                │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ SYSTEM FLOW                                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Frontend (8080) ──POST──> AI Backend (8000)            │
│       │                         │                       │
│       │                    OpenAI API                   │
│       │                         │                       │
│       │ <─────JSON─────── Scent Sequence                │
│       │                                                 │
│       │ ──Convert Names to IDs──                        │
│       │                                                 │
│       │──POST──> BLE Backend (5001)                     │
│                      │                                  │
│                 Find Device                             │
│                      │                                  │
│                 Connect BLE                             │
│                      │                                  │
│              Send Hex Commands                          │
│                      │                                  │
│              Physical Device ──> Plays Scents           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📱 Mobile Usage

The interface is fully responsive! Use on your phone:

1. Connect computer and phone to same WiFi
2. Find your computer's IP: `ifconfig | grep inet`
3. On phone, visit: `http://YOUR_IP:8080`
4. Same functionality, optimized layout!

---

## 🎨 Customization Tips

### Change Scent Durations
Edit `death_sentence/agents/schemas.py`:
```python
# Change max duration from 30 to 60 seconds
scent_duration: int = Field(ge=1, le=60)
```

### Modify AI Behavior
Edit `death_sentence/agents/prompts/system_prompt.j2`:
```jinja2
You are a death-themed scent composer...
[customize the AI's personality and instructions]
```

### Add New Scents
Edit `death_sentence/scent_classification.json`:
```json
"New Scent Name": {
    "strength": 6,
    "pleasantness": 7,
    "memories": "Your description here",
    "location": "13"
}
```

---

## 🎓 Pro Tips

1. **Sequence Testing**: Generate multiple sequences before finding perfect one
2. **Device Warm-up**: Some devices work better after first use
3. **Intensity**: Longer durations = stronger scent perception
4. **Layering**: AI creates complementary scent transitions
5. **Save Results**: Screenshot your favorite profiles

---

## 🆘 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| "Cannot connect to 8000" | Start AI backend |
| "Cannot connect to 5001" | Start BLE backend |
| "Device not found" | Turn device ON, move closer |
| "OPENAI_API_KEY not set" | `export OPENAI_API_KEY="..."` |
| "Sequence not playing" | Check device battery |
| Page won't load | Check frontend server on 8080 |

---

## 🎉 You're Ready!

Everything is set up and integrated. Enjoy creating your death-scented experiences!

For detailed documentation, see:
- **[readme.md](readme.md)** - Quick start
- **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - Technical details
- **[INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)** - What was changed

**Happy Death Scenting! 🌹💀**


