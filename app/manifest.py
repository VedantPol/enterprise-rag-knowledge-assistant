import json
from pathlib import Path
from threading import Lock


class ManifestStore:
    def __init__(self, path: Path):
        self.path = path
        self._lock = Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("{}", encoding="utf-8")

    def all(self) -> dict:
        with self._lock:
            return json.loads(self.path.read_text(encoding="utf-8") or "{}")

    def upsert(self, source_id: str, record: dict) -> None:
        with self._lock:
            data = json.loads(self.path.read_text(encoding="utf-8") or "{}")
            data[source_id] = record
            self.path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

    def clear(self) -> None:
        with self._lock:
            self.path.write_text("{}", encoding="utf-8")
