"""Generate a larger inert dataset for scanner benchmarking and evaluation.

This script creates a collection of zip archives representing Python package candidates.
It is designed for static-only scanning and intentionally never imports or executes
any generated artifact.
"""

from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = ROOT / "dataset_generated_large"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def safe_module(name: str) -> str:
    return (
        f'"""Harmless module for {name}."""\n\n'
        "def add(a, b):\n"
        "    return a + b\n\n"
        "def format_value(value):\n"
        "    return f'hello {value}'\n"
    )


def suspicious_module(name: str) -> str:
    return (
        f'"""Demo suspicious-looking module for {name}."""\n\n'
        "import os\n"
        "import subprocess\n"
        "\n"
        "def run_check():\n"
        "    os.system('echo benign-check')\n"
        "    subprocess.run(['echo', 'benign-check'], check=False)\n"
        "    return 'ok'\n"
    )


def malformed_module(name: str) -> str:
    return (
        f'"""Malformed source for {name}."""\n\n'
        "def broken(:\n"
        "    return 'bad signature'\n"
    )


def build_script(name: str) -> str:
    return (
        f'"""Build script placeholder for {name}."""\n\n'
        "import os\n"
        "\n"
        "def configure():\n"
        "    os.system('echo configure')\n"
        "    return 'configured'\n"
    )


def pyproject_text(name: str) -> str:
    return (
        "[build-system]\n"
        "requires = [\"setuptools\"]\n"
        "build-backend = \"setuptools.build_meta\"\n\n"
        f"[project]\n"
        f"name = \"{name}\"\n"
        "version = \"0.1.0\"\n"
        "description = \"Synthetic inert metadata\"\n"
    )


def metadata_text(name: str) -> str:
    return (
        f"Name: {name}\n"
        "Version: 0.1.0\n"
        "Summary: Synthetic metadata for static analysis\n"
        "Author: SupplyGuard\n"
    )


def typosquat_name(name: str) -> str:
    return (
        f'"""Typosquat-like module for {name}."""\n\n'
        "def normalize(value):\n"
        "    return value.strip().lower()\n"
    )


def make_zip_from_files(source_dir: Path, archive_path: Path) -> None:
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(source_dir.rglob("*")):
            if file_path.is_file():
                zf.write(file_path, arcname=file_path.relative_to(source_dir))


def build_artifact(class_dir: Path, artifact_name: str, files: dict[str, str], extra_traversal: dict[str, str] | None = None) -> None:
    artifact_dir = class_dir / artifact_name
    artifact_dir.mkdir(parents=True, exist_ok=True)
    for filename, content in files.items():
        write_text(artifact_dir / filename, content)
    if extra_traversal:
        for filename, content in extra_traversal.items():
            write_text(artifact_dir / filename, content)
    make_zip_from_files(artifact_dir, class_dir / f"{artifact_name}.zip")


def generate() -> None:
    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    dataset = {
        "dataset_version": "0.2.0",
        "dataset_identifier": "generated-large-inert-package-dataset",
        "description": "Larger synthetic dataset for static-only evaluation of SupplyGuard.",
        "artifact_format": "zip",
        "classes": {
            "benign": {"label": 0, "count": 4},
            "suspicious": {"label": 1, "count": 4},
            "malformed": {"label": 1, "count": 3},
            "traversal": {"label": 1, "count": 3},
            "build_scripts": {"label": 1, "count": 3},
            "typosquat": {"label": 0, "count": 3},
            "metadata_only": {"label": 0, "count": 3},
        },
        "notes": "All generated files are inert placeholders and never executed or imported.",
    }

    class_sets = {
        "benign": ["alpha_pkg", "beta_pkg", "gamma_pkg", "delta_pkg"],
        "suspicious": ["sus_a_pkg", "sus_b_pkg", "sus_c_pkg", "sus_d_pkg"],
        "malformed": ["bad_a_pkg", "bad_b_pkg", "bad_c_pkg"],
        "traversal": ["t_a_pkg", "t_b_pkg", "t_c_pkg"],
        "build_scripts": ["b_a_pkg", "b_b_pkg", "b_c_pkg"],
        "typosquat": ["reqeusts_pkg", "numpyy_pkg", "djanog_pkg"],
        "metadata_only": ["meta_a_pkg", "meta_b_pkg", "meta_c_pkg"],
    }

    for class_name, artifact_names in class_sets.items():
        class_dir = OUTPUT_ROOT / class_name
        class_dir.mkdir(parents=True, exist_ok=True)
        for artifact_name in artifact_names:
            if class_name == "benign":
                build_artifact(class_dir, artifact_name, {"module.py": safe_module(artifact_name)})
            elif class_name == "suspicious":
                build_artifact(class_dir, artifact_name, {"module.py": suspicious_module(artifact_name)})
            elif class_name == "malformed":
                build_artifact(class_dir, artifact_name, {"module.py": malformed_module(artifact_name)})
            elif class_name == "traversal":
                build_artifact(
                    class_dir,
                    artifact_name,
                    {"module.py": safe_module(artifact_name)},
                    extra_traversal={
                        "../escape.py": "print('not run')\n",
                        "/tmp/unsafe.py": "print('not run')\n",
                    },
                )
            elif class_name == "build_scripts":
                build_artifact(
                    class_dir,
                    artifact_name,
                    {
                        "module.py": build_script(artifact_name),
                        "pyproject.toml": pyproject_text(artifact_name),
                    },
                )
            elif class_name == "typosquat":
                build_artifact(class_dir, artifact_name, {"module.py": typosquat_name(artifact_name)})
            elif class_name == "metadata_only":
                build_artifact(class_dir, artifact_name, {"PKG-INFO": metadata_text(artifact_name)})

    manifest_path = OUTPUT_ROOT / "manifest.json"
    manifest_path.write_text(json.dumps(dataset, indent=2, sort_keys=True), encoding="utf-8")

    readme = OUTPUT_ROOT / "README.md"
    readme.write_text(
        "# Larger synthetic inert dataset\n\n"
        "This dataset is intended for static-only evaluation.\n"
        "Artifacts are zip archives containing inert placeholder package content.\n"
        "These files are never imported or executed.\n",
        encoding="utf-8",
    )

    print(f"Generated dataset at: {OUTPUT_ROOT}")
    print(json.dumps(dataset, indent=2, sort_keys=True))


if __name__ == "__main__":
    generate()
