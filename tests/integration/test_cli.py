import os
import subprocess
import sys


def test_version_command():
    env = os.environ.copy()
    env['PYTHONPATH'] = r'C:\Users\Latitude\SupplyGuard\src' + os.pathsep + env.get('PYTHONPATH', '')
    process = subprocess.run(
        [sys.executable, '-m', 'supplyguard.cli', 'version'],
        capture_output=True,
        text=True,
        cwd='C:\\Users\\Latitude\\SupplyGuard',
        env=env,
        check=False,
    )
    assert process.returncode == 0
    assert 'SupplyGuard' in process.stdout
