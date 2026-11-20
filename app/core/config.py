"""Application configuration manager with local persistence."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .constants import (
    APP_NAME,
    DEFAULT_PING_TARGET,
    DEFAULT_UPDATE_INTERVAL_MS,
    DEFAULT_TIMEOUT_SEC,
)


def _default_config_dir() -> Path:
    """Return platform-appropriate config directory."""
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / APP_NAME


def _default_data_dir() -> Path:
    """Return platform-appropriate data directory."""
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / APP_NAME


class Config:
    """Thread-safe-ish configuration store (main-thread oriented)."""

    DEFAULTS: dict[str, Any] = {
        "ping_target": DEFAULT_PING_TARGET,
        "update_interval_ms": DEFAULT_UPDATE_INTERVAL_MS,
        "timeout_sec": DEFAULT_TIMEOUT_SEC,
        "theme": "dark",
        "language": "pt_BR",
        "notifications_enabled": True,
        "notify_on_high_latency": True,
        "latency_threshold_ms": 100.0,
        "notify_on_packet_loss": True,
        "packet_loss_threshold_pct": 5.0,
        "history_retention_days": 30,
        "auto_start_monitoring": False,
        "window_geometry": None,
        "window_state": None,
        "last_export_dir": str(Path.home()),
    }

    def __init__(self) -> None:
        self.config_dir = _default_config_dir()
        self.data_dir = _default_data_dir()
        self.config_file = self.config_dir / "config.json"
        self.db_path = self.data_dir / "history.db"
        self._data: dict[str, Any] = {}
        self._ensure_dirs()
        self.load()

    def _ensure_dirs(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def load(self) -> None:
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    self._data = {**self.DEFAULTS, **loaded}
                    return
            except (json.JSONDecodeError, OSError):
                pass
        self._data = dict(self.DEFAULTS)

    def save(self) -> None:
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except OSError:
            pass  # non-fatal

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, self.DEFAULTS.get(key, default))

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def update(self, mapping: dict[str, Any]) -> None:
        self._data.update(mapping)

    def reset_to_defaults(self) -> None:
        self._data = dict(self.DEFAULTS)
        self.save()

    # Convenience properties
    @property
    def ping_target(self) -> str:
        return str(self.get("ping_target"))

    @ping_target.setter
    def ping_target(self, value: str) -> None:
        self.set("ping_target", value)

    @property
    def update_interval_ms(self) -> int:
        return int(self.get("update_interval_ms"))

    @update_interval_ms.setter
    def update_interval_ms(self, value: int) -> None:
        self.set("update_interval_ms", max(200, int(value)))


_config_instance: Config | None = None


def get_config() -> Config:
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
