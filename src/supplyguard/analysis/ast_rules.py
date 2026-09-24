"""AST-based static analysis rules."""

from __future__ import annotations

import ast
from pathlib import Path

from supplyguard.config import ScannerConfig
from supplyguard.models import Finding


DANGEROUS_CALLS = {
    "os.system": "OS_SYSTEM",
    "subprocess.run": "SUBPROCESS_RUN",
    "subprocess.Popen": "SUBPROCESS_POPEN",
    "subprocess.call": "SUBPROCESS_CALL",
    "eval": "EVAL",
    "exec": "EXEC",
    "pickle.loads": "PICKLE_LOADS",
    "importlib.import_module": "IMPORTLIB_IMPORT_MODULE",
    "ctypes.CDLL": "CTYPES_CDLL",
}


class DangerousCallVisitor(ast.NodeVisitor):
    def __init__(self, file_path: str, module_name: str):
        self.file_path = file_path
        self.module_name = module_name
        self.findings: list[Finding] = []

    def _record(self, node: ast.AST, call_name: str):
        self.findings.append(
            Finding(
                finding_id=f"{self.module_name}:{call_name}:{getattr(node, 'lineno', 0)}",
                module=self.module_name,
                rule_id=call_name,
                category="dynamic_execution",
                severity="HIGH",
                confidence="MEDIUM",
                score_contribution=40,
                file_path=self.file_path,
                line_number=getattr(node, "lineno", None),
                evidence=call_name,
                explanation="Static analysis identified a call capable of executing external commands or dynamic code.",
                recommendation="Review the call in context; treat it as a high-risk import-time or runtime execution primitive.",
            )
        )

    def visit_Call(self, node: ast.Call):
        call_name = self._resolve_call_name(node.func)
        if call_name in DANGEROUS_CALLS:
            self._record(node, DANGEROUS_CALLS[call_name])
        self.generic_visit(node)

    def _resolve_call_name(self, func: ast.AST) -> str:
        if isinstance(func, ast.Attribute):
            base = self._resolve_call_name(func.value)
            if base:
                return f"{base}.{func.attr}"
            return func.attr
        if isinstance(func, ast.Name):
            return func.id
        return ""


def analyze_python_file(file_path: str, source_text: str, config: ScannerConfig | None = None) -> list[Finding]:
    config = config or ScannerConfig()
    findings: list[Finding] = []
    try:
        tree = ast.parse(source_text)
    except SyntaxError as exc:
        findings.append(
            Finding(
                finding_id=f"parser_error:{file_path}:{exc.lineno}",
                module=file_path,
                rule_id="PARSER_ERROR",
                category="parse_error",
                severity="MEDIUM",
                confidence="HIGH",
                score_contribution=45,
                file_path=file_path,
                line_number=getattr(exc, "lineno", None),
                evidence=str(exc),
                explanation="The source file could not be parsed, so it is not treated as clean.",
                recommendation="Inspect the file for malformed Python or syntax issues before accepting it.",
            )
        )
        return findings

    visitor = DangerousCallVisitor(file_path=file_path, module_name=Path(file_path).name)
    visitor.visit(tree)
    findings.extend(visitor.findings)
    return findings
