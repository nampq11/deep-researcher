import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
import datetime

DEFAULT_CONFIG = {
    "api": {
        "api_key": "",
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "temperature": 0,
    }
}

class Config:
    """Configuration manager."""
    
    def __init__(self):
        self._config = DEFAULT_CONFIG.copy()
        self._config_path = os.path.expanduser("~/.config/config.json")
        self._load_config()
        self._load_env_vars()
    
    def _load_config(self):
        config_path = Path(self._config_path)
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    file_config = json.load(f)
                    self._update_nested_dict(self._config, file_config)
            except Exception as e:
                print(f"Error loading config file: {e}")
    
    def _load_env_vars(self):
        if os.environ.get("API_KEY"):
            self._config["api"]["api_key"] = os.environ.get("API_KEY")
        if os.environ.get("MODEL"):
            self._config["api"]["model"] = os.environ.get("MODEL")
        if os.environ.get("TEMPERATURE"):    
            self._config["api"]["temperature"] = float(os.environ.get("TEMPERATURE"))
    
    def _update_nested_dict(self, d: Dict, u: Dict):
        for k,v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._update_nested_dict(d[k], v)
            else:
                d[k] = v
    
    def save(self):
        config_path = Path(self._config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(self._config, f, indent=2)
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        try:
            return self._config[section][key]
        except KeyError:
            return default
    
    def set(self, section: str, key: str, value: Any):
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        return self._config.get(section, {}).copy()

    def get_all(self) -> Dict[str, Any]:
        return self._config.copy()

config = Config()

def get_current_date() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d")

def get_current_datetime() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_user_agent() -> str:
    configured_agent = config.get("search", "user_agent", None)
    if configured_agent and configured_agent != "Research 1.0":
        return configured_agent

    try:
        from fake_useragent import UserAgent
        ua = UserAgent()
        return ua.random
    except ImportError:
        import random
        fake_user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
        ]
        return random.choice(fake_user_agents)
    except Exception as e:
        print(f"Error generating user agent: {e}")
        return"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"