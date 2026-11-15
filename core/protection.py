"""Watch selected user folders and report heuristic findings."""
from pathlib import Path
from threading import Lock
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from core.scanner import ScanEngine
from core.quarantine import add_to_quarantine
from core.config import load_config


class ThreatHandler(FileSystemEventHandler):
    def __init__(self, on_threat_cb=None):
        super().__init__()
        self.on_threat_cb = on_threat_cb
        self.engine = ScanEngine()
        self._recent = set()
        self._lock = Lock()

    def _check(self, path: str):
        cfg = load_config()
        if not cfg.get("rt_enabled", True):
            return
        candidate = Path(path)
        if candidate.is_symlink() or not candidate.is_file():
            return
        resolved = str(candidate.resolve())
        for exclusion in cfg.get("exclusions", []):
            if isinstance(exclusion, str) and exclusion and exclusion.casefold() in resolved.casefold():
                return
        with self._lock:
            if resolved in self._recent:
                return
            self._recent.add(resolved)
            if len(self._recent) > 512:
                self._recent.clear()
        result = self.engine._analyze_file(candidate)
        if not result:
            return
        result["reason"] = "Мониторинг в реальном времени: " + result["reason"]
        # Automatic file movement is disabled by default to avoid heuristic false-positive damage.
        if cfg.get("auto_quarantine", False):
            add_to_quarantine(result)
        if self.on_threat_cb:
            self.on_threat_cb(result)

    def on_created(self, event):
        if not event.is_directory:
            self._check(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._check(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._check(event.dest_path)


class RealTimeProtection:
    def __init__(self, on_threat_cb=None):
        self.handler = ThreatHandler(on_threat_cb)
        self.observer = None
        self.active = False

    def start(self):
        if self.active or not load_config().get("rt_enabled", True):
            return
        observer = Observer()
        paths = [Path.home() / "Downloads", Path.home() / "Desktop"]
        scheduled = 0
        for path in paths:
            if path.is_dir() and not path.is_symlink():
                observer.schedule(self.handler, str(path), recursive=True)
                scheduled += 1
        if scheduled:
            observer.start()
            self.observer = observer
            self.active = True

    def stop(self):
        if self.observer is not None and self.active:
            self.observer.stop()
            self.observer.join(timeout=5)
        self.observer = None
        self.active = False
