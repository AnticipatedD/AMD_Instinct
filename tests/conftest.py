import os
import pytest

from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def mock_env_vars():
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
    """Provides a fake OpenAI response object for router tests."""
    class FakeMessage:
        def __init__(self, content="stub response", tool_calls=None):
            self.content = content
            self.tool_calls = tool_calls or []

    class FakeChoice:
        def __init__(self):
            self.message = FakeMessage()

    class FakeResponse:
        def __init__(self):
            self.choices = [FakeChoice()]

    return FakeResponse()
