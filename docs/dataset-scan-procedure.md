# Dataset generation and scan procedure

This procedure describes how to generate a synthetic inert dataset and then scan it with SupplyGuard in a reproducible, static-only workflow.

## 1. Generate the dataset

From the project root:

```powershell
cd C:\Users\Latitude\SupplyGuard
python scripts\evaluation\generate_dataset.py
```

This creates a dataset in:

```text
C:\Users\Latitude\SupplyGuard\dataset_generated
```

For a larger benchmark set:

```powershell
python scripts\evaluation\generate_dataset_large.py
```

This creates:

```text
C:\Users\Latitude\SupplyGuard\dataset_generated_large
```

## 2. Inspect the manifest

Open the generated manifest file to confirm the class names and labels:

```text
dataset_generated/manifest.json
```

or:

```text
dataset_generated_large/manifest.json
```

Each artifact is a zip archive intended for static-only scanning. The classes are designed to include benign and suspicious samples without importing or executing any code.

## 3. Enumerate the archives

List the generated artifact files and their class folders:

```powershell
Get-ChildItem -Recurse -Filter *.zip dataset_generated | Select-Object FullName
```

or:

```powershell
Get-ChildItem -Recurse -Filter *.zip dataset_generated_large | Select-Object FullName
```

## 4. Scan a single archive

Run the scanner against one zip archive:

```powershell
python -m supplyguard.cli scan-file "C:\Users\Latitude\SupplyGuard\dataset_generated\benign\demo_pkg.zip" --json
```

You can also use the installed CLI script:

```powershell
supplyguard scan-file "C:\Users\Latitude\SupplyGuard\dataset_generated\benign\demo_pkg.zip" --json
```

## 5. Scan the full dataset

For each zip file in the generated folder, run a scan and capture the output. A simple PowerShell loop is below:

```powershell
$root = "C:\Users\Latitude\SupplyGuard\dataset_generated"
Get-ChildItem -Recurse -Filter *.zip -Path $root | ForEach-Object {
    Write-Host "Scanning $($_.FullName)"
    python -m supplyguard.cli scan-file $_.FullName --json
    Write-Host "---"
}
```

## 6. Record results

Capture each result into a JSONL or CSV file for evaluation. Suggested fields:

- sample_name
- class_label
- decision
- score
- findings_count
- scanner_version
- rule_set_version
- configuration_version

## 7. Compute evaluation metrics

Use the evaluation helper in:

```text
scripts/evaluation/metrics.py
```

A simple workflow is:

1. collect scan results into a JSON array
2. map actual labels to the dataset manifest
3. compare actual vs predicted
4. compute TP, TN, FP, FN, precision, recall, FPR, and F1

## 8. Safety rules

During the entire process:

- do not import the package
- do not execute the package
- do not run setup.py
- do not call pip install
- do not run package entry points
- do not execute any generated code

The scanner must operate on archive bytes and decoded source text only.

## 9. Recommended minimal workflow

```powershell
cd C:\Users\Latitude\SupplyGuard
python scripts\evaluation\generate_dataset.py
python -m supplyguard.cli scan-file "C:\Users\Latitude\SupplyGuard\dataset_generated\benign\demo_pkg.zip" --json
python -m supplyguard.cli scan-file "C:\Users\Latitude\SupplyGuard\dataset_generated\suspicious\danger_like_pkg.zip" --json
```

This provides a repeatable baseline evaluation loop for static-only testing.
