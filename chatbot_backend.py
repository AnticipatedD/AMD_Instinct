import json
from pathlib import Path
from typing import Dict, List, Any
import structlog
from pydantic import BaseModel, ValidationError

logger = structlog.get_logger()


class RouteRequest(BaseModel):
    prompt: str
    temperature: float


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]


class ChatbotBackendManager:
    def __init__(
        self,
        system_prompt: str = "You are an advanced platform expert guiding cluster operations.",
        config_path: str = "experiment_config.json",
    ):
        self.system_prompt = system_prompt
        self.tools: List[ToolDefinition] = []
        self.experiment_config = self._load_experiment_config(config_path)

    def _load_experiment_config(self, config_path: str) -> Dict[str, Any]:
        """Loads experiment configuration parameters for runtime consumption."""
        path = Path(config_path)
        if path.exists():
            try:
                with open(path, "r") as f:
                    config = json.load(f)
                    logger.info("experiment_config_loaded", path=config_path)
                    return config
            except Exception as e:
                logger.error("experiment_config_load_failed", error=str(e))
        return {}

    def create_initial_conversation(self, initial_user_input: str) -> List[Dict[str, str]]:
        """Constructs structurally sound conversation arrays pinning structural frames."""
        if not initial_user_input.strip():
            logger.error("initial_conversation_failed", error="Empty user input")
            raise ValueError("Initial user seed payload strings cannot be empty configuration inputs.")
        conversation = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": initial_user_input},
        ]
        logger.info("initial_conversation_created", conversation=conversation)
        return conversation

    def get_sampling_params(self, runtime_mode: str = "precise") -> Dict[str, Any]:
        """Maps token profile variables matching deterministic execution patterns, incorporating experiment config."""
        model_params = self.experiment_config.get("model_parameters", {})
        default_seed = self.experiment_config.get("seed", 42)

        if runtime_mode == "precise":
            params = {
                "temperature": model_params.get("temperature", 0.0),
                "top_p": model_params.get("top_p", 0.1),
                "max_tokens": model_params.get("max_tokens", 1024),
                "presence_penalty": 0.0,
                "seed": default_seed,
            }
        elif runtime_mode == "creative":
            params = {
                "temperature": 0.8,
                "top_p": 0.9,
                "max_tokens": 2048,
                "presence_penalty": 0.3,
                "seed": default_seed,
            }
        else:
            params = {
                "temperature": model_params.get("temperature", 0.7),
                "top_p": model_params.get("top_p", 0.85),
                "max_tokens": model_params.get("max_tokens", 1024),
                "presence_penalty": 0.0,
                "seed": default_seed,
            }
        logger.info("sampling_params_selected", runtime_mode=runtime_mode, params=params)
        return params

    def register_tool(self, tool_data: Dict[str, Any]) -> None:
        """Registers a tool definition after schema validation."""
        try:
            tool = ToolDefinition(**tool_data)
            self.tools.append(tool)
            logger.info("tool_registered", tool=tool.dict())
        except ValidationError as e:
            logger.error("tool_registration_failed", error=str(e))
            raise
