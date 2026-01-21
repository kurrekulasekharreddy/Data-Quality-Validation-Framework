#!/usr/bin/env bash
set -euo pipefail
python -m dqf.cli run --rules configs/sample_rules.yaml --data-dir data/sample --out reports
echo "Wrote reports/latest_report.html and reports/latest_report.json"
