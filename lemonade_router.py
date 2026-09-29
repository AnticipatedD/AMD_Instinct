import os
import json
import structlog
from typing import Callable, Dict, List, Any, Optional
from openai import OpenAI
from pydantic import BaseModel, ValidationError

# Structured logger
import logging, structlog
structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO)
)

class RouteRequest(BaseModel):
    prompt: str
    temperature: float

class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class LemonadeRouterBuilder:
    def __init__(self, base_url: Optional[str] = None):
        """Initializes the backend routing layer engine mapping variables cleanly from environments."""
        self.api_key = os.environ.get("ROCM_API_KEY")
        self.base_url = base_url or os.environ.get("ROCM_ENGINE_URL", "http://localhost:8000/v1")

        if not self.api_key:
            raise ValueError("ROCM_API_KEY environment variable must be supplied by the operator.")

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.model_name = os.environ.get("ROCM_MODEL_NAME", "Qwen3-Coder-30B-A3B-Instruct")
        self.tools: List[Dict[str, Any]] = []
        self.tool_registry: Dict[str, Callable] = {}

    def register_tool(self, tool_data: Dict[str, Any], func: Callable) -> None:
        """Registers a structural tool routing capability execution pipeline step with schema validation."""
        try:
            tool = ToolDefinition(**tool_data)
            tool_definition = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
            self.tools.append(tool_definition)
            self.tool_registry[tool.name] = func
            logger.info("tool_registered", tool=tool.dict())
        except ValidationError as e:
            logger.error("tool_registration_failed", error=str(e))
            raise

    def route_and_execute(self, user_prompt: str, temperature: float = 0.7) -> dict:
        """Dynamically evaluates instruction bounds to route target capabilities handles."""
        try:
            request = RouteRequest(prompt=user_prompt, temperature=temperature)
        except ValidationError as e:
            logger.error("route_request_invalid", error=str(e))
            return {"status": "error", "result": f"Invalid route request: {str(e)}"}

        messages = [
            {
                "role": "system",
                "content": "You are a precise enterprise router agent. Evaluate instruction strings and route targets.",
            },
            {"role": "user", "content": request.prompt},
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=self.tools if self.tools else None,
                tool_choice="auto" if self.tools else None,
                temperature=request.temperature,
            )
            response_message = response.choices[0].message

            if hasattr(response_message, "tool_calls") and response_message.tool_calls:
                execution_logs = []
                for tool_call in response_message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)

                    if func_name in self.tool_registry:
                        runtime_output = self.tool_registry[func_name](**func_args)
                        execution_logs.append(
                            f"[Route Target: {func_name}] Executed. Output: {runtime_output}"
                        )
                        logger.info("tool_executed", tool=func_name, output=runtime_output)
                    else:
                        execution_logs.append(
                            f"[Route Error] Tool '{func_name}' is missing in registry definition."
                        )
                        logger.error("tool_missing", tool=func_name)
                return {"status": "success", "result": "\n".join(execution_logs)}

            return {"status": "success", "result": f"[Direct Fallback Route] {response_message.content}"}
        except Exception as e:
            logger.error("route_execution_failed", error=str(e))
            return {"status": "error", "result": f"[Connection Failure] Routing phase execution fault: {str(e)}"}
