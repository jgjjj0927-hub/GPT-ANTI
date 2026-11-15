"""Local demo licensing. Production-grade licensing requires server-side validation."""
from __future__ import annotations

import json
import secrets
import string
from datetime import datetime, timedelta, timezone
from core.config import HOME_DIR, atomic_write_json, get_hwid, load_config, save_config

LICENSE_DB = HOME_DIR / "licenses.json"
TARIFS = {
    "trial": {"name": "Trial", "days": 7, "price": 0},
    "monthly": {"name": "Monthly", "days": 30, "price": 149},
    "lifetime": {"name": "Lifetime", "days": None, "price": 300},
}


def _load_db() -> dict:
    try:
        value = json.loads(LICENSE_DB.read_text(encoding="utf-8"))
        if isinstance(value, dict) and isinstance(value.get("keys"), dict):
            return value
    except (OSError, UnicodeError, json.JSONDecodeError):
        pass
    return {"keys": {}}


def _save_db(data: dict) -> None:
    atomic_write_json(LICENSE_DB, data)


def issue_key(tarif: str, hwid: str) -> str:
    if tarif not in TARIFS or not isinstance(hwid, str) or len(hwid) > 128:
        return ""
    plan = TARIFS[tarif]
    db = _load_db()
    alphabet = string.ascii_uppercase + string.digits
    while True:
        key = "-".join("".join(secrets.choice(alphabet) for _ in range(4)) for _ in range(4))
        if key not in db["keys"]:
            break
    now = datetime.now(timezone.utc)
    expires = (now + timedelta(days=plan["days"])).isoformat(timespec="seconds") if plan["days"] else None
    db["keys"][key] = {"tarif": tarif, "hwid": hwid, "created": now.isoformat(timespec="seconds"), "expires": expires}
    _save_db(db)
    return key


def activate_key(key: str) -> dict:
    if not isinstance(key, str):
        return {"ok": False, "reason": "Некорректный ключ"}
    normalized = key.strip().upper()
    rec = _load_db()["keys"].get(normalized)
    if not isinstance(rec, dict):
        return {"ok": False, "reason": "Ключ не найден"}
    if rec.get("hwid") and rec["hwid"] != get_hwid():
        return {"ok": False, "reason": "Ключ привязан к другому устройству"}
    expires = rec.get("expires")
    if expires:
        try:
            expiry = datetime.fromisoformat(expires)
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            if expiry < datetime.now(timezone.utc):
                return {"ok": False, "reason": "Срок действия ключа истёк"}
        except ValueError:
            return {"ok": False, "reason": "Повреждённая запись лицензии"}
    cfg = load_config()
    cfg.update({"activated": True, "license_key": normalized, "hwid": get_hwid()})
    save_config(cfg)
    return {"ok": True, "tarif": rec.get("tarif", "unknown"), "expires": expires}


def get_license_info() -> dict:
    cfg = load_config()
    if not cfg.get("activated") or cfg.get("hwid") != get_hwid():
        return {"active": False}
    rec = _load_db()["keys"].get(cfg.get("license_key", ""))
    if not isinstance(rec, dict):
        return {"active": False}
    expires = rec.get("expires")
    if expires:
        try:
            exp = datetime.fromisoformat(expires)
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp < datetime.now(timezone.utc):
                return {"active": False}
        except ValueError:
            return {"active": False}
    return {"active": True, "tarif": rec.get("tarif", "unknown"), "expires": expires, "is_lifetime": expires is None}
