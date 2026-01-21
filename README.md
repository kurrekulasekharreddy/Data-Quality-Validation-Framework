# Data Quality & Validation Framework (Production-Style)

A lightweight, production-oriented **Data Quality framework** that runs **config-driven validation suites** (schema, nulls, ranges, uniqueness, referential integrity, row-count reconciliation, freshness) against CSV extracts and produces **JSON + HTML** reports.

## Why this project stands out (recruiter-friendly)
- **Data Quality Gates**: stop bad data before it hits BI/ML
- **Config-driven rules**: YAML suites reusable across datasets
- **Audit-ready reporting**: structured evidence of pass/fail
- **CI-ready**: pytest + GitHub Actions
- **Extensible**: add new checks without touching the runner

## Features
- ✅ Schema checks (expected columns + types)
- ✅ Null-rate thresholds (per column)
- ✅ Numeric range checks
- ✅ Uniqueness checks (single / composite keys)
- ✅ Referential integrity checks (FK across datasets)
- ✅ Freshness checks (max age of timestamp column)
- ✅ Reports: `reports/latest_report.json` and `reports/latest_report.html`
- ✅ Exit codes for orchestration: **0 pass**, **2 fail**, **1 error**

---

## Quickstart
### 1) Install
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Run the sample suite
```bash
python -m dqf.cli run --rules configs/sample_rules.yaml --data-dir data/sample --out reports
```

### 3) View output
- `reports/latest_report.html`
- `reports/latest_report.json`

---

## Project Structure
```text
data-quality-validation-framework/
  src/dqf/                   # framework library (runner, checks, reporting)
  configs/                   # YAML rules (validation suites)
  data/sample/               # sample datasets
  reports/                   # generated reports
  tests/                     # pytest unit tests
  .github/workflows/ci.yml   # CI pipeline
  Dockerfile                 # containerized runs
```

---

## Rules YAML schema (example)
```yaml
suite_name: "finance_quality_gate"
datasets:
  - name: "customers"
    path: "customers.csv"
    checks:
      - type: "schema"
        columns:
          customer_id: "int"
          email: "str"
          created_at: "datetime"
      - type: "null_rate"
        thresholds:
          email: 0.02
      - type: "unique"
        columns: ["customer_id"]
  - name: "orders"
    path: "orders.csv"
    checks:
      - type: "range"
        column: "order_amount"
        min: 0
        max: 50000
      - type: "fk"
        column: "customer_id"
        ref_dataset: "customers"
        ref_column: "customer_id"
```

---

## Docker
```bash
docker build -t dqf .
docker run --rm -v "$PWD:/app" dqf python -m dqf.cli run --rules configs/sample_rules.yaml --data-dir data/sample --out reports
```

---

## Portfolio upgrades (ideas)
- Add DB connectors (Postgres/Snowflake) and validate tables directly
- Emit quality metrics to Prometheus / CloudWatch
- Integrate as an Airflow quality gate before downstream tasks
- Store historical reports and track data quality trends

## License
MIT
