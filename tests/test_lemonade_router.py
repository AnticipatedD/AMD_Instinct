import pytest
from unittest.mock import patch, MagicMock
from lemonade_router import LemonadeRouterBuilder


def test_tool_registration_matrix():
    """Asserts tools append cleanly to system configurations mapping elements."""
    router = LemonadeRouterBuilder()

    def target_mock_callable(target_module: str):
        return f"Compiled module path: {target_module}"

    tool_data = {
        "name": "trigger_test_compilation",
        "description": "Compiles standard HIP code blocks arrays components.",
        "parameters": {"type": "object", "properties": {"target_module": {"type": "string"}}},
    }

    router.register_tool(tool_data, target_mock_callable)

    assert "trigger_test_compilation" in router.tool_registry
    assert len(router.tools) == 1


@patch("lemonade_router.OpenAI")
def test_route_and_execute_fallback(mock_openai_class):
    """Asserts dictionary shapes return appropriately during flat text fallbacks."""
    # Fake OpenAI client returning a simple fallback message
    mock_client = MagicMock()
    fake_choice = MagicMock()
    fake_choice.message.content = "stub response"
    fake_choice.message.tool_calls = []
    mock_client.chat.completions.create.return_value.choices = [fake_choice]
    mock_openai_class.return_value = mock_client

    router = LemonadeRouterBuilder()
    output = router.route_and_execute("Hello agent, provide cluster properties details.")

    assert isinstance(output, dict)
    assert output["status"] == "success"
    assert "[Direct Fallback Route]" in output["result"]


@patch("lemonade_router.OpenAI")
def test_route_and_execute_tool_path(mock_openai_class):
    """Asserts dictionary structural integrity under operational tool target mappings."""
    # Fake OpenAI client returning a tool call
    mock_client = MagicMock()
    fake_tool_call = MagicMock()
    fake_tool_call.function.name = "trigger_test_compilation"
    fake_tool_call.function.arguments = '{"target_module": "hip_kernel_matrix"}'
    fake_choice = MagicMock()
    fake_choice.message.tool_calls = [fake_tool_call]
    mock_client.chat.completions.create.return_value.choices = [fake_choice]
    mock_openai_class.return_value = mock_client

    router = LemonadeRouterBuilder()

    def target_mock_callable(target_module: str):
        return f"SUCCESS_{target_module}"

    tool_data = {
        "name": "trigger_test_compilation",
        "description": "Description",
        "parameters": {"type": "object", "properties": {"target_module": {"type": "string"}}},
    }
    router.register_tool(tool_data, target_mock_callable)

    output = router.route_and_execute("Compile hip_kernel_matrix layout now.")

    assert isinstance(output, dict)
    assert output["status"] == "success"
    assert "SUCCESS_hip_kernel_matrix" in output["result"]
