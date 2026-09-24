"""Static analysis package."""

from .ast_rules import analyze_python_file
from .install_analysis import analyze_install_files
from .metadata import extract_metadata
from .name_similarity import analyze_name_similarity

__all__ = ["analyze_python_file", "analyze_install_files", "extract_metadata", "analyze_name_similarity"]
