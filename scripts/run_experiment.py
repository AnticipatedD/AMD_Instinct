import os
import json
import random
import torch
from pathlib import Path
import structlog

logger = structlog.get_logger()

def set_seed(seed: int) -> None:
    """Sets random seed across libraries for reproducibility."""
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    logger.info("seed_set", seed=seed)

def load_config(config_path: str = "experiment_config.json") -> dict:
    """Loads experiment configuration."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    with open(path, "r") as f:
        config = json.load(f)
    logger.info("experiment_config_loaded", path=config_path)
    return config

def run_benchmark(config: dict) -> dict:
    """Simulates a routing benchmark using configuration parameters."""
    baselines = config.get("baselines", {})
    seed = config.get("seed", 42)
    
    # Simulate deterministic metrics based on seed and baseline targets
    simulated_latency = baselines.get("latency_p95_ms", 120.0)
    simulated_throughput = baselines.get("throughput_tok_sec", 45.2)

    metrics = {
        "experiment_id": config.get("experiment_id", "exp_default"),
        "seed": seed,
        "latency_p95_ms": simulated_latency,
        "throughput_tok_sec": simulated_throughput,
        "status": "success"
    }
    return metrics

def save_metrics(metrics: dict, output_path: str = "results/metrics.json") -> None:
    """Saves output metrics deterministically."""
    out_dir = Path("results")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=2)
    logger.info("metrics_saved", path=output_path)

if __name__ == "__main__":
    config = load_config()
    set_seed(config.get("seed", 42))
    metrics = run_benchmark(config)
    save_metrics(metrics)
