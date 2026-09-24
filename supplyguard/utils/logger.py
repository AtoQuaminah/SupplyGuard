# logger.py
# Writes a structured log entry after each layer completes.
# JSON format is used so logs can be parsed programmatically later
# or reviewed manually by the user checking scan history.
# Each entry includes a UTC timestamp, the file scanned, the layer, and its output.

import json
import os
from datetime import datetime


class Logger:

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(log_dir, "scan_log.json")

    def log(self, file_path: str, layer: str, data: dict):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "file": file_path,
            "layer": layer,
            "data": data
        }
        # Append mode keeps the full scan history intact across multiple runs
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")