# SupplyGuard

SupplyGuard checks Python packages before you install them. It reads package archives as data and looks for risky Python calls, suspicious install or build files, unsafe archive paths, malformed source, and package-name issues.

The scanner is deliberately static. It does not import the package, run its code, run `setup.py`, or install anything from the package being checked.

## Requirements

- Python 3.11 or newer
- PowerShell or Command Prompt on Windows, or a normal shell on macOS/Linux

## Install from a clone

Clone the repository and enter its directory:

```powershell
git clone https://github.com/YOUR-ACCOUNT/SupplyGuard.git
cd SupplyGuard
```

Install SupplyGuard in editable mode:

```powershell
python -m pip install -e .
```

Check that the command is available:

```powershell
supplyguard version
```

On Windows, `py -m pip install -e .` and `py -m supplyguard.cli ...` can be used when `python` is not the selected command.

## Scan a package from PyPI

Give the scanner the package name:

```powershell
supplyguard scan requests
```

The scanner retrieves the package artifact and analyzes it locally. Use `--json` when another script or a CI job needs structured output:

```powershell
supplyguard scan requests --json
```

This requires network access to retrieve the package metadata and artifact.

## Scan a local package file

Use `scan-file` for a wheel, source distribution, or supported archive already on disk:

```powershell
supplyguard scan-file .\downloads\some_package-1.0.0-py3-none-any.whl
```

For JSON output:

```powershell
supplyguard scan-file .\downloads\some_package-1.0.0.tar.gz --json
```

The command prints the decision, score, and findings. The decisions are:

- `ALLOW`: no configured risk was found
- `WARN`: the package needs review
- `BLOCK`: the package contains findings that meet the blocking threshold

The process exit code is also useful in automation: `0` means `ALLOW`, `1` means `WARN`, and `2` means `BLOCK`.

## Run without installing the command

From the repository root, the module form also works:

```powershell
python -m supplyguard.cli scan-file .\path\to\package.whl --json
```

If the package has not been installed, set the source directory first in PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m supplyguard.cli scan-file .\path\to\package.whl --json
```

## Run the included tests

```powershell
python -m pytest -q
```

## Try the generated test dataset

The repository includes inert synthetic archives for checking the scanner without using real third-party packages.

Generate the standard dataset:

```powershell
python scripts\evaluation\generate_dataset.py
```

Generate the larger dataset:

```powershell
python scripts\evaluation\generate_dataset_large.py
```

Scan all generated archives and write the results to `dataset_scan_summary.json`:

```powershell
python scripts\evaluation\scan_dataset.py
```

The complete repeatable workflow is documented in [docs/dataset-scan-procedure.md](docs/dataset-scan-procedure.md).

## What SupplyGuard checks

- Python source with AST-based rules for risky calls such as `os.system`, `subprocess`, and `eval`-style execution
- `setup.py`, `setup.cfg`, and `pyproject.toml` install/build configuration
- Archive paths, traversal attempts, symlinks, and extraction limits
- Package metadata and name similarity
- A deterministic score with an explainable decision

## Safety and current scope

SupplyGuard is a proof-of-concept static scanner. It does not prove that a package is safe, and static analysis cannot see every runtime behavior. Do not install or execute a package merely because it receives an `ALLOW` result.

The scanner's safety boundary is important: candidate code is treated as untrusted bytes and text. Do not run package entry points, `setup.py`, build hooks, or installation commands as part of an evaluation.

## Project layout

- `src/supplyguard/`: scanner and command-line application
- `tests/`: unit, security, regression, and CLI tests
- `scripts/evaluation/`: dataset generation, scanning, and metrics helpers
- `docs/`: design notes and repeatable evaluation procedures
