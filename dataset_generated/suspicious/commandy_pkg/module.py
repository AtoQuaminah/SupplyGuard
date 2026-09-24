"""Suspicious-looking demo content for commandy_pkg."""

import os
import subprocess

def run_demo():
    os.system('echo harmless-demo')
    subprocess.run(['echo', 'harmless-demo'], check=False)
    return 'done'
