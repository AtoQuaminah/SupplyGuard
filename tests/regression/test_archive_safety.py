import zipfile

from supplyguard.scanner import scan_file


def test_archive_traversal_is_blocked(tmp_path):
    archive = tmp_path / 'traversal.zip'
    with zipfile.ZipFile(archive, 'w') as zf:
        zf.writestr('../../escape.py', 'print("escape")\n')

    result = scan_file(str(archive))

    assert result['decision'] == 'BLOCK'
    assert result['score'] >= 50
