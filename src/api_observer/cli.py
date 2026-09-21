from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from . import __version__
from .core import run_check, validate_check
from .storage import HistoryStore

DEFAULT_DB = Path.home() / ".api-observer" / "history.db"


def load_config(path: str) -> list[dict]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read config: {exc}") from exc
    checks = data.get("checks") if isinstance(data, dict) else None
    if not isinstance(checks, list) or not checks:
        raise ValueError("config must contain a non-empty 'checks' array")
    for check in checks:
        validate_check(check)
    return checks


def execute(checks: list[dict], store: HistoryStore, as_json: bool) -> int:
    results = [run_check(check) for check in checks]
    store.add_many(results)
    if as_json:
        print(json.dumps([r.to_dict() for r in results], ensure_ascii=False, indent=2))
    else:
        for r in results:
            icon = "PASS" if r.ok else "FAIL"
            status = r.status if r.status is not None else "-"
            print(f"{icon:4} {r.name:24} status={status} latency={r.latency_ms:.1f}ms  {r.message}")
    return 0 if all(r.ok for r in results) else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="api-observer", description="Dependency-free HTTP API health monitor")
    p.add_argument("--version", action="version", version=__version__)
    p.add_argument("--db", default=str(DEFAULT_DB), help="SQLite history path")
    sub = p.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run configured checks once")
    run.add_argument("config")
    run.add_argument("--json", action="store_true")
    watch = sub.add_parser("watch", help="run checks repeatedly until interrupted")
    watch.add_argument("config")
    watch.add_argument("--interval", type=float, default=60)
    watch.add_argument("--json", action="store_true")
    hist = sub.add_parser("history", help="show recent check history")
    hist.add_argument("--limit", type=int, default=50)
    hist.add_argument("--json", action="store_true")
    prune = sub.add_parser("prune", help="delete old history")
    prune.add_argument("--keep-days", type=int, default=30)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        store = HistoryStore(args.db)
        if args.command in {"run", "watch"}:
            checks = load_config(args.config)
            if args.command == "run":
                return execute(checks, store, args.json)
            if not 1 <= args.interval <= 86400:
                raise ValueError("interval must be between 1 and 86400 seconds")
            try:
                while True:
                    execute(checks, store, args.json)
                    time.sleep(args.interval)
            except KeyboardInterrupt:
                return 0
        if args.command == "history":
            rows = store.recent(args.limit)
            if args.json:
                print(json.dumps(rows, indent=2))
            else:
                for row in rows:
                    print(f"{'PASS' if row['ok'] else 'FAIL':4} {row['name']:24} status={row['status']} latency={row['latency_ms']:.1f}ms")
            return 0
        deleted = store.prune(args.keep_days)
        print(f"Deleted {deleted} history rows.")
        return 0
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    finally:
        if "store" in locals():
            store.close()


if __name__ == "__main__":
    raise SystemExit(main())
