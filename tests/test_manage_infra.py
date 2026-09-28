import pytest
from unittest.mock import patch, MagicMock
import subprocess
import manage_infra


def test_verify_rocm_environment_success():
    """Ensures ROCm environment verification passes when rocm-smi returns driver info."""
    with patch("shutil.which", return_value="/usr/bin/rocm-smi"), \
         patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(stdout="Driver v1.0")
        result = manage_infra.verify_rocm_environment()
        assert result is True
        mock_run.assert_called_once()


def test_verify_rocm_environment_missing_binary():
    """Ensures ROCm environment verification fails when rocm-smi is missing."""
    with patch("shutil.which", return_value=None):
        result = manage_infra.verify_rocm_environment()
        assert result is False


def test_verify_rocm_environment_subprocess_error():
    """Ensures ROCm environment verification fails on subprocess error."""
    with patch("shutil.which", return_value="/usr/bin/rocm-smi"), \
         patch("subprocess.run", side_effect=subprocess.SubprocessError("fail")):
        result = manage_infra.verify_rocm_environment()
        assert result is False


def test_check_kubernetes_cluster_success():
    """Ensures Kubernetes cluster check passes when kubectl cluster-info succeeds."""
    with patch("shutil.which", return_value="/usr/bin/kubectl"), \
         patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock()
        result = manage_infra.check_kubernetes_cluster()
        assert result is True
        mock_run.assert_called_once()


def test_check_kubernetes_cluster_missing_binary():
    """Ensures Kubernetes cluster check fails when kubectl is missing."""
    with patch("shutil.which", return_value=None):
        result = manage_infra.check_kubernetes_cluster()
        assert result is False


def test_check_kubernetes_cluster_subprocess_error():
    """Ensures Kubernetes cluster check fails on subprocess error."""
    with patch("shutil.which", return_value="/usr/bin/kubectl"), \
         patch("subprocess.run", side_effect=subprocess.SubprocessError("fail")):
        result = manage_infra.check_kubernetes_cluster()
        assert result is False


def test_deploy_manifests_success():
    """Ensures manifests are applied successfully when kubectl apply runs cleanly."""
    with patch("manage_infra.check_kubernetes_cluster", return_value=True), \
         patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock()
        result = manage_infra.deploy_manifests(["manifest.yaml"])
        assert result is True
        mock_run.assert_called_with(["kubectl", "apply", "-f", "manifest.yaml"], check=True)


def test_deploy_manifests_failure():
    """Ensures deploy_manifests fails when kubectl apply raises error."""
    with patch("manage_infra.check_kubernetes_cluster", return_value=True), \
         patch("subprocess.run", side_effect=subprocess.SubprocessError("fail")):
        result = manage_infra.deploy_manifests(["manifest.yaml"])
        assert result is False
