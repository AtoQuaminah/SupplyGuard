"""Configuration for the SupplyGuard scanner."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

DEFAULT_MAX_ARCHIVE_SIZE = 100 * 1024 * 1024
DEFAULT_MAX_EXTRACTED_SIZE = 150 * 1024 * 1024
DEFAULT_MAX_FILES = 2000


@dataclass
class ScannerConfig:
    """Deterministic implementation baseline configuration."""

    max_archive_size_bytes: int = DEFAULT_MAX_ARCHIVE_SIZE
    max_extracted_size_bytes: int = DEFAULT_MAX_EXTRACTED_SIZE
    max_member_count: int = DEFAULT_MAX_FILES
    allow_network: bool = False
    dangerous_calls: tuple[str, ...] = (
        "os.system",
        "subprocess.run",
        "subprocess.Popen",
        "subprocess.call",
        "eval",
        "exec",
        "pickle.loads",
        "importlib.import_module",
        "ctypes.CDLL",
    )
    install_script_candidates: tuple[str, ...] = (
        "setup.py",
        "pyproject.toml",
        "setup.cfg",
    )
    score_warning_threshold: int = 35
    score_block_threshold: int = 70
    name_similarity_threshold: float = 0.75
    allowed_extensions: tuple[str, ...] = (".py", ".toml", ".cfg", ".txt", ".md", ".rst", ".json")
    scanner_version: str = "0.1.0"
    rule_set_version: str = "baseline-0.1"
    configuration_version: str = "baseline-0.1"
    metadata: dict[str, Any] = field(default_factory=dict)


DEFAULT_CONFIG = ScannerConfig()
