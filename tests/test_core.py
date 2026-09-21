import json
from unittest.mock import patch

import pytest

from api_observer.core import CheckResult, _json_path, run_check, validate_check
from api_observer.storage import HistoryStore


class FakeResponse:
    status = 200
    def __init__(self, body=b'{"status":"ok","data":{"count":2}}'):
        self.body = body
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self, n=-1): return self.body[:n]


def test_json_path_nested():
    assert _json_path({"a": [{"b": 7}]}, "a.0.b") == 7


def test_validate_rejects_non_http():
    with pytest.raises(ValueError):
        validate_check({"name": "bad", "url": "file:///etc/passwd"})

@patch("api_observer.core.urllib.request.urlopen", return_value=FakeResponse())
def test_run_check_json_assertion(mock_open):
    result = run_check({"name": "health", "url": "https://example.test/health", "json_path": "status", "json_equals": "ok"})
    assert result.ok and result.status == 200

@patch("api_observer.core.urllib.request.urlopen", return_value=FakeResponse())
def test_run_check_json_mismatch(mock_open):
    result = run_check({"name": "health", "url": "https://example.test", "json_path": "data.count", "json_equals": 3})
    assert not result.ok and "mismatch" in result.message

@patch("api_observer.core.urllib.request.urlopen", return_value=FakeResponse(b"service healthy"))
def test_body_regex(mock_open):
    result = run_check({"name": "health", "url": "https://example.test", "body_regex": "healthy$"})
    assert result.ok


def test_history_roundtrip_and_prune(tmp_path):
    store = HistoryStore(tmp_path / "history.db")
    result = CheckResult("api", "https://example.test", True, 200, 12.5, "ok", 1.0)
    store.add_many([result])
    rows = store.recent(10)
    assert rows[0]["name"] == "api" and rows[0]["ok"] is True
    assert store.prune(0) == 1
    store.close()
