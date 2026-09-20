import os
import pytest

@pytest.fixture(autouse=True)
def mock_env_vars():
    os.environ["ROCM_API_KEY"] = "mock_key_123"
    os.environ["ROCM_ENGINE_URL"] = "http://localhost:8000/v1"
    os.environ["ROCM_MODEL_NAME"] = "mock_amd_model"
