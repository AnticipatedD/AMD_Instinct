import subprocess
import shutil
import requests
import structlog
from typing import Dict, Any

logger = structlog.get_logger()

def verify_rocm_environment() -> bool:
    """Verifies that rocm-smi is available and functional."""
    if not shutil.which("rocm-smi"):
        logger.error("rocm_smi_missing")
        return False
    try:
        result = subprocess.run(["rocm-smi"], capture_output=True, text=True, check=True)
        logger.info("rocm_environment_verified", output=result.stdout.strip())
        return True
    except subprocess.SubprocessError as e:
        logger.error("rocm_environment_verification_failed", error=str(e))
        return False

def check_kubernetes_cluster() -> bool:
    """Verifies that kubectl is available and connected to a cluster."""
    if not shutil.which("kubectl"):
        logger.error("kubectl_missing")
        return False
    try:
        subprocess.run(["kubectl", "cluster-info"], capture_output=True, text=True, check=True)
        logger.info("kubernetes_cluster_verified")
        return True
    except subprocess.SubprocessError as e:
        logger.error("kubernetes_cluster_verification_failed", error=str(e))
        return False

def deploy_manifests(manifests: list[str]) -> bool:
    """Applies Kubernetes manifests if the cluster is reachable."""
    if not check_kubernetes_cluster():
        logger.error("deploy_failed_cluster_unreachable")
        return False
    
    for manifest in manifests:
        try:
            subprocess.run(["kubectl", "apply", "-f", manifest], check=True)
            logger.info("manifest_deployed", manifest=manifest)
        except subprocess.SubprocessError as e:
            logger.error("manifest_deployment_failed", manifest=manifest, error=str(e))
            return False
    return True

def health_check(engine_url: str = "http://localhost:8000/v1/models") -> Dict[str, Any]:
    """Pings the ROCm inference engine URL and returns a typed status dict."""
    try:
        response = requests.get(engine_url, timeout=2.0)
        if response.status_code == 200:
            logger.info("health_check_passed", url=engine_url, latency_ms=response.elapsed.total_seconds() * 1000)
            return {
                "status": "ok",
                "latency_ms": response.elapsed.total_seconds() * 1000
            }
        else:
            logger.warning("health_check_non_200", status_code=response.status_code)
            return {
                "status": "degraded",
                "latency_ms": response.elapsed.total_seconds() * 1000
            }
    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        return {
            "status": "error",
            "latency_ms": 0.0,
            "error": str(e)
    }
