from __future__ import annotations

import argparse
import sys

from .runner import load_suite, load_datasets, run_suite, results_to_dict
from .reporting import write_report

EXIT_PASS = 0
EXIT_FAIL = 2
EXIT_ERROR = 1

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="dqf", description="Data Quality & Validation Framework")
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run", help="Run a validation suite")
    run_p.add_argument("--rules", required=True, help="Path to YAML rules file")
    run_p.add_argument("--data-dir", required=True, help="Directory containing dataset files referenced in rules")
    run_p.add_argument("--out", default="reports", help="Output directory for reports")

    args = parser.parse_args(argv)

    try:
        suite = load_suite(args.rules)
        datasets = load_datasets(suite, args.data_dir)
        results = run_suite(suite, datasets)
        report = results_to_dict(suite.suite_name, results)
        write_report(args.out, report)

        any_fail = any(not r["passed"] for r in report["results"])
        return EXIT_FAIL if any_fail else EXIT_PASS

    except Exception as e:
        print(f"[dqf] ERROR: {e}", file=sys.stderr)
        return EXIT_ERROR

if __name__ == "__main__":
    raise SystemExit(main())
