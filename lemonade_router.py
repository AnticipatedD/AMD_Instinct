import os
import json
import logging
from typing import Callable, Dict, List, Any, Optional
from openai import OpenAI

# Initialize production-grade structured logging telemetry
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [RouterEngine] - %(message)s'
)
logger = logging.getLogger("LemonadeRouter")

class LemonadeRouterBuilder:
    def __init__(self, base_url: Optional[str] = None):
        """
        Initializes the router layer targeting Qwen3-Coder weights on AMD hardware blocks.
        """
        # Read keys directly from standard environment variables; no hardcoded fallbacks allowed
        self.api_key = os.getenv("LEMONADE_API_KEY")
        self.base_url = base_url or os.getenv("ROCM_ENGINE_URL", "http://localhost:8000/v1")
        
        if not self.api_key:
            logger.warning("LEMONADE_API_KEY environment variable is missing. Authenticated requests may fail.")
            self.api_key = "EMPTY"

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.model_name = os.getenv("ROCM_MODEL_NAME", "Qwen3-Coder-30B-A3B-Instruct")
        self.tools: List[Dict[str, Any]] = []
        self.tool_registry: Dict[str, Callable] = {}

    def register_tool(self, name: str, description: str, parameters: dict, func: Callable) -> None:
        """
        Registers structural software modules that the agent can route instructions to.
        """
        if not name or not isinstance(parameters, dict):
            raise ValueError("Invalid tool specification format passed to registry.")
            
        tool_definition = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        }
        self.tools.append(tool_definition)
        self.tool_registry[name] = func
        logger.info(f"Successfully registered system route tool: '{name}'")

    def route_and_execute(self, user_prompt: str, temperature: float = 0.7) -> dict:
        """
        Executes intent routing with GPU acceleration via HIP-optimized engine layers.
        """
        if not user_prompt.strip():
            logger.error("Empty instruction payload passed to routing layer.")
            return {"status": "error", "result": "Input instruction cannot be empty."}

        messages = [
            {
                "role": "system", 
                "content": "You are a precise enterprise router agent. Evaluate input instructions and dispatch them to the correct function tool."
            },
            {"role": "user", "content": user_prompt}
        ]
        
        logger.info(f"Dispatching intent request to model platform pipeline: {self.model_name}")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=self.tools if self.tools else None,
                tool_choice="auto" if self.tools else None,
                temperature=temperature,
                top_p=0.85
            )
            
            response_message = response.choices.message
            
            if response_message.tool_calls:
                execution_logs = []
                for tool_call in response_message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"Model selected routed trajectory: {func_name}")
                    
                    if func_name in self.tool_registry:
                        runtime_output = self.tool_registry[func_name](**func_args)
                        execution_logs.append(f"[Route Target: {func_name}] Executed. Output: {runtime_output}")
                    else:
                        execution_logs.append(f"[Route Error] Tool '{func_name}' is missing in registry definition.")
                
                return {"status": "success", "result": "\n".join(execution_logs)}
            
            return {"status": "success", "result": f"[Direct Fallback Route] {response_message.content}"}
            
        except Exception as e:
            logger.error(f"Execution error caught during model interaction: {str(e)}")
            return {"status": "error", "result": f"[Kernel Connection Error] Routing phase failed: {str(e)}"}
