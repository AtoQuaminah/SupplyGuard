import zipfile

from supplyguard.scanner import scan_file


def test_scan_file_detects_dangerous_ast(tmp_path):
    package_dir = tmp_path / "dangerous_pkg"
    package_dir.mkdir()
    (package_dir / "module.py").write_text(
        "import os\nimport subprocess\n"
        "os.system('echo hello from danger')\n"
        "subprocess.run(['bash', '-c', 'echo pwned'])\n",
        encoding="utf-8",
    )

    archive = tmp_path / "dangerous_pkg.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.write(package_dir / "module.py", arcname="module.py")

    result = scan_file(str(archive))

    assert result["decision"] in {"WARN", "BLOCK"}
    assert result["findings"]


def test_scan_file_rejects_traversal(tmp_path):
    archive = tmp_path / "bad_traversal.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("../../escape.py", "print('evil')\n")

    result = scan_file(str(archive))

    assert result["decision"] == "BLOCK"
    assert "traversal" in str(result["summary"]).lower()


def test_scan_file_does_not_execute_side_effects(tmp_path):
    package_dir = tmp_path / "safe_pkg"
    package_dir.mkdir()
    marker = tmp_path / "marker.txt"
    payload = (
        "import pathlib\n"
        "p = pathlib.Path(r'" + str(marker).replace('\\', '\\\\') + "')\n"
        "p.write_text('side-effect', encoding='utf-8')\n"
    )
    (package_dir / "module.py").write_text(payload, encoding="utf-8")

    archive = tmp_path / "safe_pkg.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.write(package_dir / "module.py", arcname="module.py")

    result = scan_file(str(archive))

    assert not marker.exists()
    assert result["decision"] in {"ALLOW", "WARN"}
