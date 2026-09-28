import json
from pathlib import Path

from supplyguard import cli


def test_scan_file_writes_json_log_and_displays_path(tmp_path, monkeypatch, capsys):
    result = {
        "package_name": "sample",
        "decision": "BLOCK",
        "score": 75,
        "findings": [{"rule_id": "TEST_RULE"}],
        "summary": "Blocked for testing.",
    }
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "scan_file", lambda path: result)

    exit_code = cli._run_scan_file("sample.whl", json_output=False)

    output = capsys.readouterr().out
    assert exit_code == 2
    assert "Log file: " in output
    log_path = Path(output.split("Log file: ", 1)[1].strip())
    assert log_path.parent.name == "logs"
    assert log_path.name.startswith("scan-")
    log_entry = json.loads(log_path.read_text(encoding="utf-8"))
    assert log_entry["scan_type"] == "scan-file"
    assert log_entry["target"] == "sample.whl"
    assert log_entry["result"] == result
    assert log_entry["elapsed_seconds"] >= 0


def test_package_scan_json_stdout_stays_machine_readable_and_logs_path(tmp_path, monkeypatch, capsys):
    result = {
        "package_name": "sample-package",
        "decision": "WARN",
        "score": 40,
        "findings": [],
        "summary": "Review recommended.",
    }
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli, "scan_package", lambda package_name: result)

    exit_code = cli._run_scan_package("sample-package", json_output=True)

    captured = capsys.readouterr()
    assert exit_code == 1
    assert json.loads(captured.out) == result
    assert "Log file: " in captured.err
    log_path = Path(captured.err.split("Log file: ", 1)[1].strip())
    assert log_path.parent.name == "logs"
    assert log_path.name.startswith("scan-")
    log_entry = json.loads(log_path.read_text(encoding="utf-8"))
    assert log_entry["scan_type"] == "scan"
    assert log_entry["target"] == "sample-package"
    assert log_entry["result"] == result