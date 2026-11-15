# ANTI-VURUS 3.2.0

Desktop demonstration application built with Python and PyQt6.

## Requirements

- Windows 10/11 (the packaged build workflow targets Windows)
- Python 3.11 or newer

## Setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` locally only if you use the optional Telegram admin bot. Set `BOT_TOKEN` and `ADMIN_ID`. Never commit or distribute `.env`; if a token was ever included in a public or shared archive, revoke it and issue a new one through Telegram's official bot management interface.

## Run

```powershell
python main.py
```

## Security notes

- The scanner uses basic heuristics; it is not a full antivirus engine and can produce false positives and false negatives.
- Real-time monitoring does not automatically quarantine files by default. Review detections before moving files to quarantine.
- Local JSON licensing is for demonstration only. It is not tamper-resistant and must not be used as a paid production licensing system without server-side validation and signed license tokens.
- Telegram bot access is restricted to the numeric `ADMIN_ID`; the former hard-coded shared password has been removed.
- Application data is stored under `~/.anti_vurus` with restrictive permissions where supported.
- Dependencies are pinned in `requirements.txt`; GitHub Actions runs `pip-audit` weekly and on pushes/pull requests.

## Build

The GitHub Actions workflow builds a Windows one-file executable. The release archive intentionally excludes `.env`, local bot state, caches, and build artifacts.
