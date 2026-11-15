""Optional Telegram admin bot. No shared password or public admin enrollment."""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path
import requests
from core.config import ADMIN_ID, BOT_TOKEN

REG_FILE = Path.home() / ".anti_vurus" / "bot_registry.json"
_session = requests.Session()
_session.trust_env = False  # Do not read .netrc credentials or implicit proxy settings.
API = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else ""


def _load_json(path: Path, default):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, type(default)) else default
    except (OSError, UnicodeError, json.JSONDecodeError):
        return default


def _api(method: str, *, timeout=10, **payload):
    if not API:
        return {}
    try:
        response = _session.post(f"{API}/{method}", json=payload, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, dict) and data.get("ok") else {}
    except (requests.RequestException, ValueError):
        return {}


def send(chat_id, message: str):
    # Plain text: untrusted device names cannot inject Telegram HTML/Markdown.
    return _api("sendMessage", chat_id=chat_id, text=str(message)[:4000])


def poll_loop(stop_event: threading.Event | None = None):
    if not BOT_TOKEN or not ADMIN_ID or not ADMIN_ID.isdigit():
        return
    stop_event = stop_event or threading.Event()
    offset = None
    backoff = 2
    while not stop_event.is_set():
        try:
            params = {"timeout": 20}
            if offset is not None:
                params["offset"] = offset
            response = _session.get(f"{API}/getUpdates", params=params, timeout=25)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict) or not payload.get("ok"):
                raise ValueError("Telegram API returned an invalid response")
            backoff = 2
            for update in payload.get("result", []):
                offset = int(update.get("update_id", 0)) + 1
                message = update.get("message") or {}
                chat = message.get("chat") or {}
                chat_id = str(chat.get("id", ""))
                if chat_id != ADMIN_ID:
                    if chat_id:
                        send(chat_id, "ÐÐ¾ÑÑÑÐ¿ Ð·Ð°Ð¿ÑÐµÑÑÐ½.")
                    continue
                text = str(message.get("text", "")).strip()
                if text == "/start" or text == "/devices":
                    registry = _load_json(REG_FILE, {})
                    lines = ["ÐÐ°ÑÐµÐ³Ð¸ÑÑÑÐ¸ÑÐ¾Ð²Ð°Ð½Ð½ÑÐµ ÑÑÑÑÐ¾Ð¹ÑÑÐ²Ð°:"]
                    for info in registry.values():
                        if isinstance(info, dict):
                            name = str(info.get("name", "unknown"))[:80]
                            lines.append(f"â¢ {name}")
                    send(chat_id, "\n".join(lines) if len(lines) > 1 else "Ð¡Ð¿Ð¸ÑÐ¾Ðº Ð¿ÑÑÑ.")
                elif text == "/help":
                    send(chat_id, "ÐÐ¾Ð¼Ð°Ð½Ð´Ñ: /start, /devices, /help")
                else:
                    send(chat_id, "ÐÐµÐ¸Ð·Ð²ÐµÑÑÐ½Ð°Ñ ÐºÐ¾Ð¼Ð°Ð½Ð´Ð°. ÐÑÐ¿Ð¾Ð»ÑÐ·ÑÐ¹ÑÐµ /help.")
        except (requests.RequestException, ValueError, TypeError):
            stop_event.wait(backoff)
            backoff = min(backoff * 2, 60)
