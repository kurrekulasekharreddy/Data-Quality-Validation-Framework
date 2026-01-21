from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List, Any

import pandas as pd
import yaml

from .config import load_suite_from_dict, SuiteSpec
from .checks import SchemaCheck, NullRateCheck, RangeCheck, UniqueCheck, ForeignKeyCheck, FreshnessCheck
from .checks.base import CheckResult

CHECK_REGISTRY = {
    "schema": SchemaCheck,
    "null_rate": NullRateCheck,
    "range": RangeCheck,
    "unique": UniqueCheck,
    "fk": ForeignKeyCheck,
    "freshness": FreshnessCheck,
}

@dataclass
class RunContext:
    suite_name: str
    datasets: Dict[str, pd.DataFrame]
    metadata: Dict[str, Any]

def _read_csv_with_types(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # heuristic datetime parsing for columns that look like timestamps
    for c in df.columns:
        if any(token in c.lower() for token in ["date", "time", "ts", "timestamp"]):
            try:
                df[c] = pd.to_datetime(df[c], errors="ignore", utc=True)
            except Exception:
                pass
    return df

def load_suite(rules_path: str) -> SuiteSpec:
    with open(rules_path, "r", encoding="utf-8") as f:
        d = yaml.safe_load(f)
    return load_suite_from_dict(d)

def load_datasets(suite: SuiteSpec, data_dir: str) -> Dict[str, pd.DataFrame]:
    datasets: Dict[str, pd.DataFrame] = {}
    for ds in suite.datasets:
        fp = os.path.join(data_dir, ds.path)
        if not os.path.exists(fp):
            raise FileNotFoundError(f"Dataset file not found: {fp}")
        datasets[ds.name] = _read_csv_with_types(fp)
    return datasets

def run_suite(suite: SuiteSpec, datasets: Dict[str, pd.DataFrame]) -> List[CheckResult]:
    ctx = RunContext(suite_name=suite.suite_name, datasets=datasets, metadata={})
    results: List[CheckResult] = []
    for ds in suite.datasets:
        for check_spec in ds.checks:
            check_cls = CHECK_REGISTRY.get(check_spec.type)
            if not check_cls:
                results.append(CheckResult(check_spec.type, ds.name, False, "Unknown check type.", {"known": list(CHECK_REGISTRY.keys())}))
                continue
            check = check_cls(ds.name, **check_spec.payload)
            try:
                results.append(check.run(ctx))
            except Exception as e:
                results.append(CheckResult(check_spec.type, ds.name, False, f"Check error: {e}", {"exception": repr(e)}))
    return results

def summarize_results(results: List[CheckResult]) -> Dict[str, Any]:
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    by_dataset: Dict[str, Dict[str, int]] = {}
    for r in results:
        by_dataset.setdefault(r.dataset, {"passed": 0, "failed": 0})
        by_dataset[r.dataset]["passed" if r.passed else "failed"] += 1
    return {"total_checks": total, "passed": passed, "failed": failed, "by_dataset": by_dataset}

def results_to_dict(suite_name: str, results: List[CheckResult]) -> Dict[str, Any]:
    return {
        "suite_name": suite_name,
        "generated_at_utc": pd.Timestamp.utcnow().isoformat(),
        "summary": summarize_results(results),
        "results": [
            {
                "check_type": r.check_type,
                "dataset": r.dataset,
                "passed": r.passed,
                "message": r.message,
                "details": r.details,
            }
            for r in results
        ],
    }
