"""Local quarantine with atomic metadata writes and path validation."""
from __future__ import annotations

import json
import os
import secrets
import shutil
from datetime import datetime, timezone
from pathlib import Path

from core.config import HOME_DIR, QUARANTINE_DIR, atomic_write_json, ensure_dirs

DB_FILE = HOME_DIR / "quarantine.json"


def _load_db() -> list:
    try:
        data = json.loads(DB_FILE.read_text(encoding="utf-8"))
        return [item for item in data if isinstance(item, dict)] if isinstance(data, list) else []
    except (OSError, UnicodeError, json.JSONDecodeError):
        return []


def _save_db(data: list) -> None:
    atomic_write_json(DB_FILE, data)


def add_to_quarantine(threat: dict) -> bool:
    try:
        ensure_dirs()
        src = Path(threat["path"]).expanduser()
        if src.is_symlink() or not src.is_file():
            return False
        resolved = src.resolve(strict=True)
        digest = str(threat.get("hash", "")).lower()
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            return False
        # Refuse to quarantine a file that changed after the scan result was produced.
        import hashlib
        actual = hashlib.sha256()
        with resolved.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                actual.update(block)
        if actual.hexdigest() != digest:
            return False
        dst = QUARANTINE_DIR / f"{digest[:16]}_{secrets.token_hex(6)}.quar"
        shutil.move(str(resolved), str(dst))
        record = dict(threat)
        record.update({"path": str(resolved), "quarantine_path": str(dst.resolve()),
                       "date_added": datetime.now(timezone.utc).isoformat()})
        db = _load_db()
        db.append(record)
        try:
            _save_db(db)
        except Exception:
            shutil.move(str(dst), str(resolved))
            raise
        return True
    except (OSError, KeyError, TypeError, ValueError):
        return False


def list_quarantine() -> list:
    return _load_db()


def _safe_quarantine_path(value: str) -> Path | None:
    try:
        root = QUARANTINE_DIR.resolve()
        candidate = Path(value)
        if candidate.is_symlink():
            return None
        path = candidate.resolve(strict=True)
        if path.parent != root or not path.is_file():
            return None
        return path
    except (OSError, RuntimeError):
        return None


def restore_file(index: int) -> bool:
    db = _load_db()
    if not isinstance(index, int) or not 0 <= index < len(db):
        return False
    item = db[index]
    q_path = _safe_quarantine_path(str(item.get("quarantine_path", "")))
    if q_path is None:
        return False
    try:
        original = Path(item.get("path", "")).expanduser()
        if not original.is_absolute():
            return False
        destination = original
        if destination.exists():
            destination = destination.with_name(f"{destination.stem}_restored{destination.suffix}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(q_path), str(destination))
        db.pop(index)
        try:
            _save_db(db)
        except Exception:
            shutil.move(str(destination), str(q_path))
            raise
        return True
    except (OSError, ValueError, TypeError):
        return False


def delete_permanently(index: int) -> bool:
    db = _load_db()
    if not isinstance(index, int) or not 0 <= index < len(db):
        return False
    q_path = _safe_quarantine_path(str(db[index].get("quarantine_path", "")))
    if q_path is None:
        return False
    original_db = list(db)
    try:
        db.pop(index)
        _save_db(db)
        try:
            q_path.unlink()
        except OSError:
            _save_db(original_db)
            raise
        return True
    except OSError:
        return False
