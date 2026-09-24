"""Suspicious-looking demo content for spawn_demo."""

import os
import subprocess

def run_demo():
    os.system('echo harmless-demo')
    subprocess.run(['echo', 'harmless-demo'], check=False)
    return 'done'
