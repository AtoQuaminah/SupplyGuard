# SupplyGuard architecture

SupplyGuard is a static-analysis-focused package scanner designed to operate on untrusted Python artifact data without importing or executing candidate code.

## Components

- Retrieval: fetches candidate artifact metadata and package files without installation.
- Artifact validation: checks archive type, size, and path safety.
- Safe extraction: writes files only inside a temporary workspace root.
- Static analysis: parses Python source with `ast` and reviews install/build scripts.
- Metadata analysis: reads package metadata fields when available.
- Name similarity: compares candidate package names against known package references using a deterministic similarity score.
- Risk scoring: sums finding contributions and converts to deterministic decision states.
- Reporting: outputs machine-readable JSON and human-readable summaries.

## Security invariants

- The candidate artifact is treated as inert data.
- No package files are imported.
- No build system is executed.
- No `pip install` operations are invoked.
- All archive members are normalized and checked before write.
