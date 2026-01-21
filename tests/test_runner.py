from dqf.runner import load_suite, load_datasets, run_suite, results_to_dict

def test_sample_suite_runs():
    suite = load_suite("configs/sample_rules.yaml")
    datasets = load_datasets(suite, "data/sample")
    results = run_suite(suite, datasets)
    report = results_to_dict(suite.suite_name, results)
    assert report["suite_name"] == "sample_quality_gate"
    assert report["summary"]["total_checks"] > 0
    # sample data intentionally includes failures (FK + negative amount)
    assert report["summary"]["failed"] >= 1
