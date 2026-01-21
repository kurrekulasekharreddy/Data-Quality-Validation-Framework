from __future__ import annotations

import pandas as pd
from typing import Dict, List
from .base import BaseCheck, CheckResult

class NullRateCheck(BaseCheck):
    check_type = "null_rate"

    def run(self, context: "RunContext") -> CheckResult:  # noqa: F821
        df = context.datasets[self.dataset_name]
        thresholds: Dict[str, float] = self.kwargs.get("thresholds", {})
        actual = {}
        failed = {}
        n = len(df)
        for col, thr in thresholds.items():
            if col not in df.columns:
                failed[col] = {"error": "column_not_found"}
                continue
            rate = float(df[col].isna().sum()) / float(n) if n else 0.0
            actual[col] = rate
            if rate > float(thr):
                failed[col] = {"threshold": float(thr), "actual": rate}
        passed = len(failed) == 0
        msg = "Null-rate thresholds satisfied." if passed else "Null-rate check failed."
        return CheckResult(self.check_type, self.dataset_name, passed, msg, {"actual": actual, "failed": failed})

class RangeCheck(BaseCheck):
    check_type = "range"

    def run(self, context: "RunContext") -> CheckResult:  # noqa: F821
        df = context.datasets[self.dataset_name]
        col = self.kwargs.get("column")
        min_v = self.kwargs.get("min")
        max_v = self.kwargs.get("max")
        if col not in df.columns:
            return CheckResult(self.check_type, self.dataset_name, False, "Range check failed: column not found.", {"column": col})
        s = pd.to_numeric(df[col], errors="coerce")
        mask = (s < min_v) | (s > max_v)
        violations = df.loc[mask, [col]].head(50)
        passed = violations.empty
        msg = "Range check passed." if passed else "Range check failed."
        return CheckResult(self.check_type, self.dataset_name, passed, msg, {
            "column": col, "min": min_v, "max": max_v,
            "num_violations": int(mask.sum()),
            "violations_sample": violations.to_dict(orient="records"),
        })

class UniqueCheck(BaseCheck):
    check_type = "unique"

    def run(self, context: "RunContext") -> CheckResult:  # noqa: F821
        df = context.datasets[self.dataset_name]
        cols: List[str] = self.kwargs.get("columns", [])
        missing = [c for c in cols if c not in df.columns]
        if missing:
            return CheckResult(self.check_type, self.dataset_name, False, "Unique check failed: missing columns.", {"missing_columns": missing})
        dup = df[df.duplicated(subset=cols, keep=False)]
        passed = dup.empty
        msg = "Uniqueness satisfied." if passed else "Uniqueness check failed."
        return CheckResult(self.check_type, self.dataset_name, passed, msg, {
            "columns": cols,
            "num_duplicates": int(len(dup)),
            "duplicates_sample": dup[cols].head(50).to_dict(orient="records"),
        })
