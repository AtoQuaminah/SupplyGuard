"""Suspicious sample that should trigger static findings without execution."""

import os
import subprocess

os.system("echo suspicious")
subprocess.run(["echo", "suspicious"], check=False)
