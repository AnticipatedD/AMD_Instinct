import os
import pytest
from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Automatically set environment variables for router tests."""
    os.environ["ROCM_API_KEY"] = "mock_key_123"
    os.environ["ROCM_ENGINE_URL"] = "http://localhost:8000/v1"
    os.environ["ROCM_MODEL_NAME"] = "mock_amd_model"


@pytest.fixture
def setup_test_env():
    """Provides a basic LemonadeRouterBuilder environment for tests."""
    from lemonade_router import LemonadeRouterBuilder
    router = LemonadeRouterBuilder(base_url="http://localhost:8000/v1")
    return router


@pytest.fixture
def mock_openai_response():
    """Provides fake OpenAI client and choice objects for router tests."""
    # Fake client
    mock_client = MagicMock()

    # Fallback choice (no tool calls, just content)
    mock_choice_fallback = MagicMock()
    mock_choice_fallback.message.content = "stub response"
    mock_choice_fallback.message.tool_calls = []

    # Tool call choice
    mock_choice_tool = MagicMock()
    fake_tool_call = MagicMock()
    fake_tool_call.function.name = "trigger_test_compilation"
    fake_tool_call.function.arguments = '{"target_module": "hip_kernel_matrix"}'
    mock_choice_tool.message.tool_calls = [fake_tool_call]

    return mock_client, mock_choice_fallback, mock_choice_tool
