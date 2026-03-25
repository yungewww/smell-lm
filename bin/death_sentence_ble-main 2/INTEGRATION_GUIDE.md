# Death Sentence + BLE Integration Guide

This guide explains how to use the integrated AI-powered scent sequence generator with your BLE device.

## Overview

The system now combines two powerful features:
1. **AI Scent Sequence Generator** - Uses OpenAI to generate death-themed scent sequences based on text input
2. **BLE Device Control** - Plays the generated sequences on your physical scent device

## Architecture

```
┌─────────────────────────┐      ┌─────────────────────────┐
│  Death Sentence AI      │      │   BLE Backend           │
│  (FastAPI on :8000)     │      │   (Flask on :5001)      │
│                         │      │                         │
│  - Generates sequences  │◄────►│  - Controls BLE device  │
│  - Frontend UI          │ CORS │  - Plays sequences      │
└─────────────────────────┘      └─────────────────────────┘
           ▲                                  │
           │                                  │
           │                                  ▼
     ┌──────────────┐                ┌──────────────┐
     │   User Text  │                │ BLE Device   │
     │    Input     │                │  (Scents)    │
     └──────────────┘                └──────────────┘
```

## Setup Instructions

### 1. Install Dependencies

First, install the required Python packages for both systems:

```bash
# Install BLE backend dependencies
pip install -r requirements.txt

# Install AI backend dependencies
cd death_sentence/agents
pip install -r requirements.txt
cd ../..
```

### 2. Configure OpenAI API Key

The AI backend requires an OpenAI API key. Set it as an environment variable:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or create a `.env` file in `death_sentence/agents/` with:
```
OPENAI_API_KEY=your-api-key-here
```

### 3. Start Both Servers

You'll need **two terminal windows** running simultaneously:

#### Terminal 1: BLE Backend (Flask)
```bash
python backend.py
```

This will start the BLE control server on `http://localhost:5001`

#### Terminal 2: AI Backend (FastAPI)
```bash
cd death_sentence/agents
uvicorn app:app --reload --port 8000
cd ../..
```

This will start the AI server on `http://localhost:8000`

### 4. Open the Frontend

Open the Death Sentence frontend in your browser:
```bash
# From project root, serve the frontend
cd death_sentence
python -m http.server 8080
```

Then navigate to: `http://localhost:8080`

## How to Use

### Step 1: Generate a Scent Sequence

1. Open `http://localhost:8080` in your browser
2. Enter a death-themed sentence, e.g., "I want to die in the forest alone.."
3. Click **"SYNTHIZE SCENT →"**
4. Wait for the AI to generate your scent sequence

### Step 2: Test Device Connection (Optional)

Before playing, you can test if your BLE device is connected:
1. After the sequence is generated, click **"🔍 TEST DEVICE CONNECTION"**
2. Ensure your device is:
   - Powered ON
   - Within Bluetooth range
   - Has "wear" in its name (or update `DEVICE_NAME_KEYWORD` in `backend.py`)

### Step 3: Play the Sequence

1. Click **"▶ PLAY SEQUENCE ON DEVICE"**
2. The system will:
   - Convert AI-generated scent names to device IDs
   - Send commands to your BLE device
   - Play each scent in sequence

## Scent Mapping

The AI generates sequences using these scent names, mapped to device locations:

| Scent Name        | Location ID | Description |
|-------------------|-------------|-------------|
| Grease            | 1           | Wood, tree, winter, forest |
| Coffin            | 2           | Playground, after the rain |
| Snaacker          | 3           | Banana, flowers, candy |
| Truncheon         | 4           | Luxury perfume, business |
| Mourning Wreath   | 5           | Lavender, relaxation |
| Grave Soil        | 6           | Poison, pollution |
| Censer            | 7           | Fashionable grandma, flower |
| Owl               | 8           | Rebirth, quiet death |
| Dead Body         | 9           | Spa spell, plantlike |
| Smudge Stick      | 10          | Meditation, eucalyptus |
| Wake Candle       | 11          | Almond tofu |
| Rotten Sweet      | 12          | Old school, ocean |

## Troubleshooting

### "Could not connect to BLE backend"
- Ensure Flask backend is running on port 5001
- Check that CORS is enabled (flask-cors installed)

### "Device not found"
- Ensure your BLE device is powered on
- Check device name contains "wear" (configurable in `backend.py`)
- Move device closer to computer

### "Network error calling composition service"
- Ensure FastAPI backend is running on port 8000
- Check OpenAI API key is set correctly

### "Location not found for scent"
- Verify `scent_classification.json` has location field for all scents
- Ensure locations are unique (1-12)

## Customization

### Change Device Keyword
Edit `backend.py`:
```python
DEVICE_NAME_KEYWORD = "wear"  # Change to match your device name
```

### Modify Scent Durations
The AI generates durations 1-30 seconds per scent, totaling 60 seconds.
Adjust in `death_sentence/agents/schemas.py`:
```python
scent_duration: int = Field(ge=1, le=30)
```

### Add New Scents
Edit `death_sentence/scent_classification.json`:
```json
"Your Scent Name": {
    "strength": 5,
    "pleasantness": 6,
    "memories": "Your description",
    "location": "13"
}
```

## API Endpoints

### BLE Backend (Flask - :5001)
- `GET /test_connection` - Test BLE device connection
- `POST /play_scent` - Play single scent
  ```json
  {"scent_id": 1, "duration": 5}
  ```
- `POST /play_sequence` - Play sequence
  ```json
  {"sequence": [{"scent_id": 1, "duration": 5}, ...]}
  ```

### AI Backend (FastAPI - :8000)
- `POST /compose` - Generate scent sequence
  ```json
  {"sentence": "I want to die in the forest alone.."}
  ```
  Returns:
  ```json
  {
    "scent_sequence": [
      {"scent_name": "Grease", "scent_duration": 15},
      ...
    ],
    "justification": "..."
  }
  ```

## Development Notes

- **Frontend**: Pure JavaScript, no build step required
- **BLE Backend**: Flask with async BLE operations via Bleak
- **AI Backend**: FastAPI with OpenAI structured outputs
- **Communication**: Cross-origin requests via CORS

## Future Enhancements

- [ ] Single unified backend (merge Flask + FastAPI)
- [ ] Real-time playback status updates
- [ ] Save/load favorite sequences
- [ ] Manual sequence editing before playback
- [ ] Volume/intensity control per scent

## Support

If you encounter issues:
1. Check console logs in browser (F12)
2. Check terminal output for both servers
3. Verify all dependencies are installed
4. Ensure device is properly paired and discoverable

Enjoy creating your death-scented experiences! 🌹💀


