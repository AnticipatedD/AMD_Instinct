import json
import os
import pytest
from pathlib import Path
import scripts.run_experiment as run_exp

def test_load_config_success():
    """Ensures experiment configuration loads correctly when file exists."""
    config = run_exp.load_config("experiment_config.json")
    assert isinstance(config, dict)
    assert config.get("seed") == 42
    assert "baselines" in config

def test_set_seed():
    """Ensures seed setting runs without exceptions."""
    try:
        run_exp.set_seed(42)
        assert True
    except Exception as e:
        pytest.fail(f"set_seed raised an exception: {e}")

def test_run_benchmark():
    """Ensures run_benchmark produces expected metrics structure."""
    config = {
        "experiment_id": "test_exp",
        "seed": 42,
        "baselines": {
            "latency_p95_ms": 100.0,
            "throughput_tok_sec": 50.0
        }
    }
    metrics = run_exp.run_benchmark(config)
    assert metrics["experiment_id"] == "test_exp"
    assert metrics["seed"] == 42
    assert metrics["latency_p95_ms"] == 100.0
    assert metrics["throughput_tok_sec"] == 50.0
    assert metrics["status"] == "success"

def test_save_metrics(tmp_path):
    """Ensures metrics are successfully saved to output path."""
    d = tmp_path / "results"
    d.mkdir()
    p = d / "metrics.json"
    
    metrics = {"status": "success", "seed": 42}
    run_exp.save_metrics(metrics, output_path=str(p))
    
    assert p.exists()
    with open(p, "r") as f:
        data = json.load(f)
    assert data["status"] == "success"
    assert data["seed"] == 42
