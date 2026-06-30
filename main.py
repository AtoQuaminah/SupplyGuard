# main.py
# Entry point for SupplyGuard. Accepts a file path as a command-line argument
# and passes it through the four-layer pipeline.
# Usage: python main.py <path_to_file>

import sys
from supplyguard.pipeline import SupplyGuardPipeline


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    pipeline = SupplyGuardPipeline()
    pipeline.scan(file_path)
