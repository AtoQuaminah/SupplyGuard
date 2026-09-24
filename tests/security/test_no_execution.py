import zipfile

from supplyguard.scanner import scan_file


def test_no_execution_marker_is_created(tmp_path):
    payload = "import pathlib\npath = pathlib.Path(r'" + str(tmp_path / 'marker.txt').replace('\\', '\\\\') + "')\npath.write_text('marker', encoding='utf-8')\n"
    archive = tmp_path / 'payload.zip'
    with zipfile.ZipFile(archive, 'w') as zf:
        zf.writestr('module.py', payload)

    result = scan_file(str(archive))

    assert not (tmp_path / 'marker.txt').exists()
    assert result['decision'] in {'ALLOW', 'WARN'}
