from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5")
    scents_path: Path = Path(os.getenv("SCENTS_JSON_PATH", PROJECT_ROOT / "scent_classification.json"))
    prompts_dir: Path = PROJECT_ROOT / "agents" / "prompts"


settings = Settings()

