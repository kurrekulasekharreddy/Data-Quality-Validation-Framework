from __future__ import annotations

from datetime import datetime, timezone, timedelta
import pandas as pd
from dateutil import parser
from .base import BaseCheck, CheckResult

class FreshnessCheck(BaseCheck):
    check_type = "freshness"

    def run(self, context: "RunContext") -> CheckResult:  # noqa: F821
        df = context.datasets[self.dataset_name]
        col = self.kwargs.get("column")
        max_age_days = int(self.kwargs.get("max_age_days", 1))

        if col not in df.columns:
            return CheckResult(self.check_type, self.dataset_name, False, "Freshness check failed: column not found.", {"column": col})

        def to_dt(x):
            if pd.isna(x):
                return None
            if isinstance(x, (datetime, pd.Timestamp)):
                dt = x.to_pydatetime() if isinstance(x, pd.Timestamp) else x
                return dt
            try:
                return parser.isoparse(str(x))
            except Exception:
                return None

        parsed = df[col].map(to_dt).dropna()
        if parsed.empty:
            return CheckResult(self.check_type, self.dataset_name, False, "Freshness check failed: no parseable timestamps.", {"column": col})

        latest = max(parsed)
        if latest.tzinfo is None:
            latest = latest.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        age = now - latest.astimezone(timezone.utc)

        passed = age <= timedelta(days=max_age_days)
        msg = "Freshness check passed." if passed else "Freshness check failed."
        return CheckResult(self.check_type, self.dataset_name, passed, msg, {
            "column": col,
            "latest_timestamp": latest.isoformat(),
            "age_days": age.total_seconds() / 86400.0,
            "max_age_days": max_age_days,
        })
