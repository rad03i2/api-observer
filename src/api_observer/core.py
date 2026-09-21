from __future__ import annotations

import json
import re
import ssl
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class CheckResult:
    name: str
    url: str
    ok: bool
    status: int | None
    latency_ms: float
    message: str
    checked_at: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _json_path(value: Any, path: str) -> Any:
    """Resolve a small, predictable dot/index path such as data.items.0.id."""
    current = value
    if not path:
        return current
    for part in path.split("."):
        if isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError) as exc:
                raise KeyError(path) from exc
        elif isinstance(current, dict) and part in current:
            current = current[part]
        else:
            raise KeyError(path)
    return current


def validate_check(check: dict[str, Any]) -> None:
    if not isinstance(check, dict):
        raise ValueError("each check must be an object")
    if not isinstance(check.get("name"), str) or not check["name"].strip():
        raise ValueError("check.name must be a non-empty string")
    url = check.get("url")
    if not isinstance(url, str) or not url.startswith(("http://", "https://")):
        raise ValueError(f"{check['name']}: url must use http:// or https://")
    method = str(check.get("method", "GET")).upper()
    if method not in {"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE"}:
        raise ValueError(f"{check['name']}: unsupported method {method}")
    timeout = check.get("timeout", 10)
    if not isinstance(timeout, (int, float)) or not 0 < timeout <= 120:
        raise ValueError(f"{check['name']}: timeout must be > 0 and <= 120")
    expected = check.get("expected_status", 200)
    if not isinstance(expected, (int, list)):
        raise ValueError(f"{check['name']}: expected_status must be an integer or list")
    if "body_regex" in check:
        re.compile(str(check["body_regex"]))


def run_check(check: dict[str, Any]) -> CheckResult:
    validate_check(check)
    name, url = check["name"].strip(), check["url"]
    method = str(check.get("method", "GET")).upper()
    headers = {str(k): str(v) for k, v in check.get("headers", {}).items()}
    body = check.get("body")
    data = None
    if body is not None:
        if isinstance(body, (dict, list)):
            data = json.dumps(body).encode()
            headers.setdefault("Content-Type", "application/json")
        else:
            data = str(body).encode()
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    started = time.perf_counter()
    status: int | None = None
    raw = b""
    try:
        context = ssl.create_default_context()
        with urllib.request.urlopen(request, timeout=float(check.get("timeout", 10)), context=context) as response:
            status = response.status
            raw = response.read(int(check.get("max_body_bytes", 1_000_000)) + 1)
    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read(int(check.get("max_body_bytes", 1_000_000)) + 1)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        elapsed = (time.perf_counter() - started) * 1000
        return CheckResult(name, url, False, status, elapsed, f"request failed: {exc}", time.time())

    elapsed = (time.perf_counter() - started) * 1000
    max_bytes = int(check.get("max_body_bytes", 1_000_000))
    if len(raw) > max_bytes:
        return CheckResult(name, url, False, status, elapsed, f"response exceeded {max_bytes} bytes", time.time())

    expected = check.get("expected_status", 200)
    allowed = [expected] if isinstance(expected, int) else expected
    if status not in allowed:
        return CheckResult(name, url, False, status, elapsed, f"expected status {allowed}, got {status}", time.time())
    max_latency = check.get("max_latency_ms")
    if max_latency is not None and elapsed > float(max_latency):
        return CheckResult(name, url, False, status, elapsed, f"latency {elapsed:.1f} ms exceeded {max_latency} ms", time.time())

    text = raw.decode("utf-8", errors="replace")
    if "body_regex" in check and not re.search(str(check["body_regex"]), text):
        return CheckResult(name, url, False, status, elapsed, "body_regex did not match", time.time())
    if "json_path" in check:
        try:
            parsed = json.loads(text)
            actual = _json_path(parsed, str(check["json_path"]))
        except (json.JSONDecodeError, KeyError) as exc:
            return CheckResult(name, url, False, status, elapsed, f"JSON assertion failed: {exc}", time.time())
        if "json_equals" in check and actual != check["json_equals"]:
            return CheckResult(name, url, False, status, elapsed, f"JSON value mismatch: {actual!r}", time.time())
    return CheckResult(name, url, True, status, elapsed, "ok", time.time())
