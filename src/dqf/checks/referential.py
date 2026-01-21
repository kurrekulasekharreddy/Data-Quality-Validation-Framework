from __future__ import annotations

from .base import BaseCheck, CheckResult

class ForeignKeyCheck(BaseCheck):
    check_type = "fk"

    def run(self, context: "RunContext") -> CheckResult:  # noqa: F821
        df = context.datasets[self.dataset_name]
        col = self.kwargs.get("column")
        ref_ds = self.kwargs.get("ref_dataset")
        ref_col = self.kwargs.get("ref_column")

        if col not in df.columns:
            return CheckResult(self.check_type, self.dataset_name, False, "FK check failed: column not found.", {"column": col})
        if ref_ds not in context.datasets:
            return CheckResult(self.check_type, self.dataset_name, False, "FK check failed: ref dataset not loaded.", {"ref_dataset": ref_ds})

        ref_df = context.datasets[ref_ds]
        if ref_col not in ref_df.columns:
            return CheckResult(self.check_type, self.dataset_name, False, "FK check failed: ref column not found.", {"ref_column": ref_col})

        left = df[col].dropna()
        right = set(ref_df[ref_col].dropna().unique().tolist())
        invalid = left[~left.isin(right)]

        passed = invalid.empty
        msg = "Referential integrity satisfied." if passed else "Referential integrity failed."
        return CheckResult(self.check_type, self.dataset_name, passed, msg, {
            "column": col,
            "ref_dataset": ref_ds,
            "ref_column": ref_col,
            "num_invalid": int(len(invalid)),
            "invalid_sample": invalid.head(50).tolist(),
        })
