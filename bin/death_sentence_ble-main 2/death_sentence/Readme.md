### Backend (FastAPI)

1) Set API key

```bash
export OPENAI_API_KEY="<your-openai-api-key>"  # required
```

2) Create venv, install deps, run server (from repo root)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r agents/requirements.txt
uvicorn agents.app:app --reload --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

### Frontend (Static files)

Serve the files from the repo root and open the app in a browser.

```bash
python3 -m http.server 5500
```

Then visit:

```
http://localhost:5500/index.html
```

