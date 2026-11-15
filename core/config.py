"""Application configuration and safe local persistence."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import socket
import tempfile
import uuid
from pathlib import Path
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent.parent
# .env is a local developer convenience only; it is excluded from release archives.
load_dotenv(PROJECT_DIR / ".env", override=False)

APP_NAME = "ANTI-VURUS"
APP_VERSION = "3.2.0"
HOME_DIR = Path.home() / ".anti_vurus"
QUARANTINE_DIR = HOME_DIR / "quarantine"
CONFIG_FILE = HOME_DIR / "config.json"
KEY_FILE = HOME_DIR / "license.key"
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = os.getenv("ADMIN_ID", "").strip()

DEFAULT_CONFIG = {
    "activated": False,
    "license_key": "",
    "hwid": "",
    "theme": "dark",
    "rt_enabled": True,
    "auto_quarantine": False,
    "exclusions": [],
}


def ensure_dirs() -> None:
    HOME_DIR.mkdir(parents=True, exist_ok=True)
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        try:
            HOME_DIR.chmod(0o700)
            QUARANTINE_DIR.chmod(0o700)
        except OSError:
            pass


def atomic_write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
        if os.name != "nt":
            try:
                path.chmod(0o600)
            except OSError:
                pass
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_config() -> dict:
    ensure_dirs()
    try:
        raw = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            cfg = dict(DEFAULT_CONFIG)
            cfg.update(raw)
            cfg["exclusions"] = [x for x in cfg.get("exclusions", []) if isinstance(x, str)] if isinstance(cfg.get("exclusions"), list) else []
            cfg["rt_enabled"] = cfg.get("rt_enabled", True) is True
            cfg["auto_quarantine"] = cfg.get("auto_quarantine", False) is True
            cfg["activated"] = cfg.get("activated", False) is True
            for key in ("license_key", "hwid", "theme"):
                if not isinstance(cfg.get(key), str):
                    cfg[key] = DEFAULT_CONFIG[key]
            return cfg
    except (OSError, UnicodeError, json.JSONDecodeError):
        pass
    return dict(DEFAULT_CONFIG)


def save_config(cfg: dict) -> None:
    if not isinstance(cfg, dict):
        raise TypeError("Configuration must be a dictionary")
    safe = dict(DEFAULT_CONFIG)
    safe.update(cfg)
    atomic_write_json(CONFIG_FILE, safe)


def get_hwid() -> str:
    """Return a stable, non-reversible device identifier without shell commands."""
    cfg = load_config()
    cached = cfg.get("hwid")
    if isinstance(cached, str) and len(cached) == 32:
        return cached
    material = "|".join((platform.node(), platform.machine(), platform.system(), str(uuid.getnode())))
    hwid = sha256(material)[:32]
    cfg["hwid"] = hwid
    save_config(cfg)
    return hwid


def get_pc_name() -> str:
    return socket.gethostname()


def is_activated() -> bool:
    cfg = load_config()
    return bool(cfg.get("activated") and cfg.get("hwid") == get_hwid())
