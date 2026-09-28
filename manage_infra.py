import subprocess
import shutil
import structlog
import sys
from typing import List

# Structured logger
logger = structlog.get_logger()


def verify_rocm_environment() -> bool:
    """Verifies if local hardware contains functional AMD ROCm paths."""
    logger.info("check_rocm_start", message="Checking for local AMD GPU hardware interfaces...")
    smi_path = shutil.which("rocm-smi")
    if not smi_path:
        logger.warning("rocm_smi_missing", message="rocm-smi execution binary not found in system PATH")
        return False

    try:
        result = subprocess.run(
            [smi_path, "--showdriverversion"],
            capture_output=True,
            text=True,
            check=True,
        )
        logger.info("rocm_smi_verified", driver=result.stdout.strip())
        return True
    except subprocess.SubprocessError as e:
        logger.error("rocm_smi_failed", error=str(e))
        return False


def check_kubernetes_cluster() -> bool:
    """Verifies connection status to target Kubernetes API layer environments."""
    kubectl_path = shutil.which("kubectl")
    if not kubectl_path:
        logger.error("kubectl_missing", message="kubectl CLI binary not found")
        return False

    try:
        subprocess.run([kubectl_path, "cluster-info"], capture_output=True, check=True)
        logger.info("k8s_cluster_connected", message="Successfully connected to Kubernetes cluster")
        return True
    except subprocess.SubprocessError as e:
        logger.error("k8s_cluster_unreachable", error=str(e))
        return False


def deploy_manifests(manifest_paths: List[str]) -> bool:
    """Applies Kubernetes manifest configurations directly to the system cluster."""
    if not check_kubernetes_cluster():
        return False

    for path in manifest_paths:
        logger.info("apply_manifest_start", manifest=path)
        try:
            subprocess.run(["kubectl", "apply", "-f", path], check=True)
            logger.info("apply_manifest_success", manifest=path)
        except subprocess.SubprocessError as e:
            logger.error("apply_manifest_failed", manifest=path, error=str(e))
            return False
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        success = verify_rocm_environment()
        sys.exit(0 if success else 1)
