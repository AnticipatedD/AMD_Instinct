import json
import os

def test_experiment_reproducibility_config():
    assert os.path.exists("experiment_config.json")
    with open("experiment_config.json") as f:
        data = json.load(f)
    assert data["seed"] == 42
    assert "baselines" in data
