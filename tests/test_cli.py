import json
from unittest.mock import patch

import pytest

from api_observer.cli import load_config, main
from api_observer.core import CheckResult


def test_load_config(tmp_path):
    path = tmp_path / "checks.json"
    path.write_text(json.dumps({"checks": [{"name": "x", "url": "https://example.test"}]}))
    assert load_config(str(path))[0]["name"] == "x"


def test_empty_config_rejected(tmp_path):
    path = tmp_path / "checks.json"
    path.write_text('{"checks": []}')
    with pytest.raises(ValueError):
        load_config(str(path))

@patch("api_observer.cli.run_check")
def test_run_exit_nonzero_on_failure(run_check, tmp_path):
    config = tmp_path / "checks.json"
    config.write_text(json.dumps({"checks": [{"name": "x", "url": "https://example.test"}]}))
    run_check.return_value = CheckResult("x", "https://example.test", False, 500, 1.0, "bad", 1.0)
    assert main(["--db", str(tmp_path / "db.sqlite"), "run", str(config)]) == 1
