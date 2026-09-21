from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from .core import CheckResult


class HistoryStore:
    def __init__(self, path: str | Path):
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("""CREATE TABLE IF NOT EXISTS checks (
            id INTEGER PRIMARY KEY,
            checked_at REAL NOT NULL,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            ok INTEGER NOT NULL,
            status INTEGER,
            latency_ms REAL NOT NULL,
            message TEXT NOT NULL
        )""")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_checks_name_time ON checks(name, checked_at DESC)")
        self.db.commit()

    def add_many(self, results: Iterable[CheckResult]) -> None:
        self.db.executemany(
            "INSERT INTO checks(checked_at,name,url,ok,status,latency_ms,message) VALUES(?,?,?,?,?,?,?)",
            [(r.checked_at, r.name, r.url, int(r.ok), r.status, r.latency_ms, r.message) for r in results],
        )
        self.db.commit()

    def recent(self, limit: int = 50) -> list[dict]:
        if not 1 <= limit <= 10_000:
            raise ValueError("limit must be between 1 and 10000")
        rows = self.db.execute("SELECT * FROM checks ORDER BY checked_at DESC, id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(row) | {"ok": bool(row["ok"])} for row in rows]

    def prune(self, keep_days: int) -> int:
        if keep_days < 0:
            raise ValueError("keep_days cannot be negative")
        cur = self.db.execute("DELETE FROM checks WHERE checked_at < unixepoch('now') - ? * 86400", (keep_days,))
        self.db.commit()
        return cur.rowcount

    def close(self) -> None:
        self.db.close()
