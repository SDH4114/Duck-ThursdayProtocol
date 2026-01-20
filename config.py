"""
Configuration management for Duck.
Config stored in ~/.config/duck/config.json
"""

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path


def get_config_dir() -> Path:
    """Get config directory, create if needed."""
    config_dir = Path.home() / ".config" / "duck"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


CONFIG_FILE = get_config_dir() / "config.json"


@dataclass
class LauncherConfig:
    target_directory: str = "~"
    terminal_app: str = "Terminal"
    agent_command: str = "gemini"
    voice_key: str = "F5"
    
    def get_expanded_directory(self) -> str:
        return os.path.expanduser(self.target_directory)


def load_config() -> LauncherConfig:
    """Load config from ~/.config/duck/config.json"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
            # Handle old configs without voice_key
            if "hotkey" in data and "voice_key" not in data:
                data["voice_key"] = "F5"
                del data["hotkey"]
            return LauncherConfig(**data)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Config error: {e}")
    return LauncherConfig()


def save_config(config: LauncherConfig) -> None:
    """Save config to ~/.config/duck/config.json"""
    with open(CONFIG_FILE, "w") as f:
        json.dump(asdict(config), f, indent=2)
    print(f"Config saved to {CONFIG_FILE}")


def get_available_terminals() -> list[str]:
    return ["Terminal", "Ghostty", "iTerm", "Warp", "kitty", "alacritty"]


def get_available_agents() -> list[str]:
    return ["gemini", "claude", "codex", "aider"]
