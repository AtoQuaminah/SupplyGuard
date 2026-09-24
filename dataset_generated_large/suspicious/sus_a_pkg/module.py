"""Demo suspicious-looking module for sus_a_pkg."""

import os
import subprocess

def run_check():
    os.system('echo benign-check')
    subprocess.run(['echo', 'benign-check'], check=False)
    return 'ok'
