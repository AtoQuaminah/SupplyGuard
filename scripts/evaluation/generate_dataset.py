"""Generate a synthetic inert dataset of package artifacts for scanner testing.

This script creates a dataset_generated/ directory under the project root and writes
multiple zip archives representing package candidates. The files are generated as
harmless placeholders and are never executed or imported by the scanner.
"""

from __future__ import annotations

import json
import os
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = ROOT / "dataset_generated"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_safe_module(name: str) -> str:
    return (
        f'"""Harmless module for {name}."""\n\n'
        f"def add(a, b):\n"
        f"    return a + b\n\n"
        f"def greet(value):\n"
        f"    return f'hello {{value}}'\n"
    )


def make_suspicious_module(name: str) -> str:
    return (
        f'"""Suspicious-looking demo content for {name}."""\n\n'
        "import os\n"
        "import subprocess\n"
        "\n"
        "def run_demo():\n"
        "    os.system('echo harmless-demo')\n"
        "    subprocess.run(['echo', 'harmless-demo'], check=False)\n"
        "    return 'done'\n"
    )


def make_malformed_module(name: str) -> str:
    return (
        f'"""Malformed demo content for {name}."""\n\n'
        "def broken(:\n"
        "    return 'missing params'\n"
    )


def make_build_script(name: str) -> str:
    return (
        f'"""Build metadata placeholder for {name}."""\n\n'
        "import os\n"
        "import subprocess\n"
        "\n"
        "def configure():\n"
        "    os.system('echo setup step')\n"
        "    return 'configured'\n"
    )


def make_toml_metadata(name: str) -> str:
    return (
        "[build-system]\n"
        "requires = [\"setuptools\"]\n"
        "build-backend = \"setuptools.build_meta\"\n\n"
        f"[project]\n"
        f"name = \"{name}\"\n"
        "version = \"0.1.0\"\n"
        "description = \"Synthetic inert metadata\"\n"
    )


def make_typosquat_module(name: str) -> str:
    return (
        f'"""Typosquat-like demo for {name}."""\n\n'
        "def normalize(x):\n"
        "    return x.strip().lower()\n"
    )


def make_metadata_only(name: str) -> str:
    return (
        f"Name: {name}\n"
        "Version: 0.1.0\n"
        "Summary: Synthetic metadata-only package\n"
        "Author: SupplyGuard Test\n"
    )


def zip_directory(source_dir: Path, archive_path: Path) -> None:
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(source_dir.rglob("*")):
            if file_path.is_file():
                zf.write(file_path, arcname=file_path.relative_to(source_dir))


def create_artifact(class_dir: Path, artifact_name: str, source_files: dict[str, str], extra_entries: dict[str, str] | None = None) -> None:
    artifact_dir = class_dir / artifact_name
    artifact_dir.mkdir(parents=True, exist_ok=True)
    for filename, content in source_files.items():
        write_text(artifact_dir / filename, content)
    if extra_entries:
        for filename, content in extra_entries.items():
            write_text(artifact_dir / filename, content)
    archive_path = class_dir / f"{artifact_name}.zip"
    zip_directory(artifact_dir, archive_path)


def build_dataset() -> None:
    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    manifest = {
        "dataset_version": "0.1.0",
        "dataset_identifier": "generated-inert-package-dataset",
        "description": "Synthetic inert dataset for static scanner evaluation. All files are data only and are never executed.",
        "artifact_format": "zip",
        "classes": {
            "benign": {"label": 0, "count": 3},
            "suspicious": {"label": 1, "count": 3},
            "malformed": {"label": 1, "count": 2},
            "traversal": {"label": 1, "count": 2},
            "build_scripts": {"label": 1, "count": 2},
            "typosquat": {"label": 0, "count": 2},
            "metadata_only": {"label": 0, "count": 2},
        },
        "notes": "All artifacts are intentionally inert and designed to be scanned statically without imports or execution.",
    }

    classes = {
        "benign": ["demo_pkg", "safe_lib", "plain_project"],
        "suspicious": ["danger_like_pkg", "spawn_demo", "commandy_pkg"],
        "malformed": ["broken_pkg", "invalid_syntax_pkg"],
        "traversal": ["path_traversal_pkg", "escape_pkg"],
        "build_scripts": ["build_risk_pkg", "install_risk_pkg"],
        "typosquat": ["requesst_pkg", "numppy_pkg"],
        "metadata_only": ["meta_pkg", "info_pkg"],
    }

    for class_name, names in classes.items():
        class_dir = OUTPUT_ROOT / class_name
        class_dir.mkdir(parents=True, exist_ok=True)
        for artifact_name in names:
            if class_name == "benign":
                create_artifact(class_dir, artifact_name, {"module.py": make_safe_module(artifact_name)})
            elif class_name == "suspicious":
                create_artifact(class_dir, artifact_name, {"module.py": make_suspicious_module(artifact_name)})
            elif class_name == "malformed":
                create_artifact(class_dir, artifact_name, {"module.py": make_malformed_module(artifact_name)})
            elif class_name == "traversal":
                create_artifact(
                    class_dir,
                    artifact_name,
                    {"module.py": make_safe_module(artifact_name)},
                    extra_entries={"../escape.py": "print('not executed')\n", "/tmp/abs_escape.py": "print('not executed')\n"},
                )
            elif class_name == "build_scripts":
                create_artifact(
                    class_dir,
                    artifact_name,
                    {
                        "module.py": make_build_script(artifact_name),
                        "pyproject.toml": make_toml_metadata(artifact_name),
                    },
                )
            elif class_name == "typosquat":
                create_artifact(class_dir, artifact_name, {"module.py": make_typosquat_module(artifact_name)})
            elif class_name == "metadata_only":
                create_artifact(class_dir, artifact_name, {"PKG-INFO": make_metadata_only(artifact_name)})

    manifest_path = OUTPUT_ROOT / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    readme = OUTPUT_ROOT / "README.md"
    readme.write_text(
        "# Synthetic inert dataset\n\n"
        "This dataset is intended for static-only evaluation of SupplyGuard.\n"
        "The files are inert and may be scanned as archive contents but must never be imported or executed.\n",
        encoding="utf-8",
    )

    print(f"Dataset generated at: {OUTPUT_ROOT}")
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    build_dataset()
