import pytest
from unittest.mock import patch, MagicMock
import manage_infra

def test_health_check_success():
    """Ensures health_check returns status 'ok' and latency when engine returns 200."""
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.elapsed.total_seconds.return_value = 0.05
        mock_get.return_value = mock_response

        result = manage_infra.health_check("http://localhost:8000/v1/models")
        assert result["status"] == "ok"
        assert result["latency_ms"] == 50.0
        mock_get.assert_called_once_with("http://localhost:8000/v1/models", timeout=2.0)

def test_health_check_degraded():
    """Ensures health_check returns status 'degraded' when engine returns non-200."""
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.elapsed.total_seconds.return_value = 0.08
        mock_get.return_value = mock_response

        result = manage_infra.health_check("http://localhost:8000/v1/models")
        assert result["status"] == "degraded"
        assert result["latency_ms"] == 80.0

def test_health_check_exception():
    """Ensures health_check handles connection errors gracefully and returns 'error' status."""
    with patch("requests.get", side_effect=Exception("Connection refused")):
        result = manage_infra.health_check("http://localhost:8000/v1/models")
        assert result["status"] == "error"
        assert "Connection refused" in result["error"]
        assert result["latency_ms"] == 0.0
