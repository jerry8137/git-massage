import os
import tomllib
import tomli_w
from pathlib import Path
from typing import Optional, Dict, Any

APP_NAME = "git-massage"
CONFIG_DIR = Path.home() / ".config" / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.toml"

DEFAULT_CONFIG = {
    "model": "gpt-5-nano",
    "max_diff_lines": 500,
}


def _ensure_config_dir() -> None:
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, Any]:
    config = DEFAULT_CONFIG.copy()

    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "rb") as f:
                file_config = tomllib.load(f)
                config.update(file_config)
        except Exception:
            pass

    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        config["openai_api_key"] = env_key

    env_model = os.getenv("GIT_MASSAGE_MODEL")
    if env_model:
        config["model"] = env_model

    return config


def save_config(key: str, value: Any) -> None:
    _ensure_config_dir()

    current_config = {}
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "rb") as f:
                current_config = tomllib.load(f)
        except Exception:
            pass

    current_config[key] = value

    with open(CONFIG_FILE, "wb") as f:
        tomli_w.dump(current_config, f)


def get_api_key(config: Dict[str, Any]) -> Optional[str]:
    return config.get("openai_api_key")
