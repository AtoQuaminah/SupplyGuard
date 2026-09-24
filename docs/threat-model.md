# Threat model

## Assets protected

- The local workstation.
- The scanner runtime environment.
- The trusted project configuration.
- Local source checkpoints and reproduction artifacts.

## Threats considered

- Archive traversal via `..` or absolute paths.
- Symlink-based writes outside the extraction root.
- Zip bombs or oversized archives.
- `os.system`, `subprocess`, and `eval` style execution primitives.
- Build hooks and installation scripts that may spawn commands.

## Assumptions

- Candidate artifacts are untrusted until they pass static validation.
- The scanner is not a sandbox and intentionally does not execute candidate code.
- The default policy is secure-by-default and deterministic.
