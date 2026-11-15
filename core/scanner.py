"""Bounded heuristic scanner. It is not a substitute for a signature-based AV engine."""
from __future__ import annotations

import hashlib
import math
import os
import subprocess
import threading
from collections import Counter
from pathlib import Path

MAX_FILE_SIZE = 100 * 1024 * 1024
MAX_FILES = 10000
DANGEROUS_EXTENSIONS = {".exe", ".dll", ".bat", ".cmd", ".vbs", ".ps1", ".scr", ".com"}


class ScanEngine:
    def __init__(self, progress_cb=None, found_cb=None, done_cb=None):
        self.progress_cb = progress_cb
        self.found_cb = found_cb
        self.done_cb = done_cb
        self._stop_event = threading.Event()
        self._thread = None
        self._stopped = False

    def start(self, target_path: str) -> bool:
        if self._thread and self._thread.is_alive():
            return False
        target = Path(target_path).expanduser()
        if not target.exists():
            raise FileNotFoundError(target)
        self._stop_event.clear()
        self._stopped = False
        self._thread = threading.Thread(target=self._run_scan, args=(target,), daemon=True, name="anti-vurus-scan")
        self._thread.start()
        return True

    def stop(self) -> None:
        self._stopped = True
        self._stop_event.set()

    @staticmethod
    def _calc_entropy(data: bytes) -> float:
        if not data:
            return 0.0
        counts = Counter(data)
        length = len(data)
        return -sum((count / length) * math.log2(count / length) for count in counts.values())

    @staticmethod
    def _check_signature(path: Path) -> bool:
        """Check Authenticode without interpolating an untrusted path into a command."""
        if os.name != "nt":
            return False
        script = "$p = [Console]::In.ReadToEnd(); (Get-AuthenticodeSignature -LiteralPath $p).Status"
        try:
            result = subprocess.run(
                ["powershell.exe", "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", script],
                input=str(path), capture_output=True, text=True, timeout=5, check=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            return result.returncode == 0 and result.stdout.strip() == "Valid"
        except (OSError, subprocess.TimeoutExpired):
            return False

    def _analyze_file(self, file_path: Path):
        try:
            if file_path.is_symlink() or not file_path.is_file():
                return None
            stat = file_path.stat()
            if stat.st_size <= 0 or stat.st_size > MAX_FILE_SIZE:
                return None
            with file_path.open("rb") as stream:
                sample = stream.read(8192)
            is_pe = sample.startswith(b"MZ")
            entropy = self._calc_entropy(sample)
            ext = file_path.suffix.lower()
            digest = hashlib.sha256()
            with file_path.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(block)
            reasons = []
            severity = "Средняя"
            if is_pe and entropy >= 7.6 and not self._check_signature(file_path):
                reasons.append("Высокая энтропия PE-файла без подтверждённой подписи")
                severity = "Средняя"
            elif ext in DANGEROUS_EXTENSIONS and not is_pe:
                # Extension alone is not evidence of malware; keep the finding low confidence.
                reasons.append("Исполняемый/скриптовый формат требует проверки")
                severity = "Низкая"
            if not reasons:
                return None
            return {
                "path": str(file_path.resolve()), "name": file_path.name,
                "severity": severity, "type": "Эвристика", "reason": " | ".join(reasons),
                "hash": digest.hexdigest(), "size": stat.st_size,
                "confidence": "низкая; требуется ручная проверка",
            }
        except (OSError, PermissionError):
            return None

    @staticmethod
    def _collect_files(target: Path):
        if target.is_symlink():
            return []
        if target.is_file():
            return [target]
        files = []
        for root, dirs, names in os.walk(target, followlinks=False):
            dirs[:] = [d for d in dirs if not (Path(root) / d).is_symlink()]
            for name in names:
                candidate = Path(root) / name
                if not candidate.is_symlink():
                    files.append(candidate)
                    if len(files) >= MAX_FILES:
                        return files
        return files

    def _run_scan(self, target: Path) -> None:
        found = []
        try:
            files = self._collect_files(target)
            total = max(len(files), 1)
            for index, file_path in enumerate(files):
                if self._stop_event.is_set():
                    break
                result = self._analyze_file(file_path)
                if result:
                    found.append(result)
                    if self.found_cb:
                        self.found_cb(result)
                if self.progress_cb:
                    self.progress_cb(int((index + 1) * 100 / total))
        finally:
            if self.done_cb:
                self.done_cb(found, self._stopped)
