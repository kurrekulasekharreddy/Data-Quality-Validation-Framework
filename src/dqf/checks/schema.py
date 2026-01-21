from __future__ import annotations

from typing import Any, Dict
from .base import BaseCheck, CheckResult

_TYPE_MAP = {
    "int": "int",
    "float": "float",
    "str": "object",
    "datetime": "datetime64[ns]",
    "bool": "bool",
}

def _normalize_dtype(dtype: Any) -> str:
    s = str(dtype)
    if s.startswith("datetime64"):
        return "datetime64[ns]"
    if s.startswith("int"):
        return "int"
    if s.startswith("float"):
        return "float"
    if s == "object":
        return "object"
    if s == "bool":
        return "bool"
    return s

class SchemaCheck(BaseCheck):
    check_type = "schema"

    def run(self, context: "RunContext") -> CheckResult:  # noqa: F821
        df = context.datasets[self.dataset_name]
        expected: Dict[str, str] = self.kwargs.get("columns", {})
        missing = [c for c in expected.keys() if c not in df.columns]
        extra = [c for c in df.columns if c not in expected.keys()]

        type_mismatches = {}
        for col, t in expected.items():
            if col not in df.columns:
                continue
            exp = _TYPE_MAP.get(t, t)
            got = _normalize_dtype(df[col].dtype)
            # allow int->float when nulls force upcast
            if exp == "int" and got.startswith("float"):
                continue
            if exp == "datetime64[ns]" and "datetime64" in got:
                continue
            if exp != got:
                type_mismatches[col] = {"expected": exp, "got": got}

        passed = (len(missing) == 0) and (len(type_mismatches) == 0)
        msg = "Schema matches expected columns/types." if passed else "Schema check failed."
        return CheckResult(
            check_type=self.check_type,
            dataset=self.dataset_name,
            passed=passed,
            message=msg,
            details={"missing_columns": missing, "extra_columns": extra, "type_mismatches": type_mismatches},
        )
