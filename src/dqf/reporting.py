from __future__ import annotations

import json
import os
from typing import Any, Dict
from jinja2 import Template

_HTML = Template('''<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Data Quality Report - {{ suite_name }}</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; }
    .summary { margin-bottom: 16px; padding: 12px; border: 1px solid #ddd; border-radius: 8px; }
    table { border-collapse: collapse; width: 100%; margin-top: 12px; }
    th, td { border: 1px solid #ddd; padding: 8px; vertical-align: top; }
    th { background: #f6f6f6; }
    .pass { color: #0a7a0a; font-weight: bold; }
    .fail { color: #b00020; font-weight: bold; }
    .small { color: #555; font-size: 12px; }
    code { background: #f3f3f3; padding: 2px 4px; border-radius: 4px; }
    details { max-width: 100%; }
    pre { white-space: pre-wrap; word-break: break-word; }
  </style>
</head>
<body>
  <h1>Data Quality Report</h1>
  <div class="small">Suite: <code>{{ suite_name }}</code> | Generated: <code>{{ generated_at_utc }}</code></div>

  <div class="summary">
    <div><strong>Total checks:</strong> {{ summary.total_checks }} | <span class="pass">Passed:</span> {{ summary.passed }} | <span class="fail">Failed:</span> {{ summary.failed }}</div>
    <div class="small">By dataset:</div>
    <ul class="small">
    {% for ds, counts in summary.by_dataset.items() %}
      <li><code>{{ ds }}</code> — Passed: {{ counts.passed }}, Failed: {{ counts.failed }}</li>
    {% endfor %}
    </ul>
  </div>

  <table>
    <thead>
      <tr>
        <th>Dataset</th>
        <th>Check</th>
        <th>Status</th>
        <th>Message</th>
        <th>Details</th>
      </tr>
    </thead>
    <tbody>
      {% for r in results %}
      <tr>
        <td><code>{{ r.dataset }}</code></td>
        <td><code>{{ r.check_type }}</code></td>
        <td>{% if r.passed %}<span class="pass">PASS</span>{% else %}<span class="fail">FAIL</span>{% endif %}</td>
        <td>{{ r.message }}</td>
        <td>
          <details>
            <summary class="small">view</summary>
            <pre class="small">{{ r.details | tojson(indent=2) }}</pre>
          </details>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</body>
</html>''')

def write_report(out_dir: str, report: Dict[str, Any]) -> Dict[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    json_path = os.path.join(out_dir, "latest_report.json")
    html_path = os.path.join(out_dir, "latest_report.html")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(_HTML.render(**report))

    return {"json": json_path, "html": html_path}
