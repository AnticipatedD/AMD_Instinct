import pytest
from pydantic import ValidationError
from chatbot_backend import ChatbotBackendManager, ToolDefinition


def test_create_initial_conversation_structure():
    """Validates structural properties returned by configuration frame initializers."""
    manager = ChatbotBackendManager(system_prompt="Custom System Context Operator Verification")
    conversation = manager.create_initial_conversation("Verify device 0 state parameters.")

    assert isinstance(conversation, list)
    assert len(conversation) == 2
    assert conversation[0]["role"] == "system"
    assert conversation[0]["content"] == "Custom System Context Operator Verification"
    assert conversation[1]["role"] == "user"
    assert conversation[1]["content"] == "Verify device 0 state parameters."


def test_create_initial_conversation_empty_error():
    """Asserts logic blocks generate execution exception warnings on missing spaces."""
    manager = ChatbotBackendManager()
    with pytest.raises(ValueError, match="cannot be empty configuration inputs"):
        manager.create_initial_conversation("    ")


def test_get_sampling_params_mapping():
    """Asserts tuning configuration parameters match specific hardware runtime constraints."""
    manager = ChatbotBackendManager()

    precise_profile = manager.get_sampling_params("precise")
    assert precise_profile["temperature"] == 0.0
    assert precise_profile["top_p"] == 0.1

    creative_profile = manager.get_sampling_params("creative")
    assert creative_profile["temperature"] == 0.8
    assert creative_profile["presence_penalty"] == 0.3

    default_profile = manager.get_sampling_params("unrecognized_fallback_mode")
    assert default_profile["temperature"] == 0.7


def test_register_tool_success():
    """Ensures tool registration succeeds with valid schema."""
    manager = ChatbotBackendManager()
    tool_data = {
        "name": "sample_tool",
        "description": "A sample tool for testing",
        "parameters": {"type": "object", "properties": {"param": {"type": "string"}}},
    }
    manager.register_tool(tool_data)
    assert len(manager.tools) == 1
    assert manager.tools[0].name == "sample_tool"


def test_register_tool_invalid_schema():
    """Ensures invalid tool schema raises ValidationError."""
    manager = ChatbotBackendManager()
    bad_tool_data = {
        "name": "",  # invalid name
        "description": "Broken tool",
        "parameters": "not_a_dict",  # invalid parameters type
    }
    with pytest.raises(ValidationError):
        manager.register_tool(bad_tool_data)
