import os
import json
from typing import Callable, Dict, List, Any
from openai import OpenAI

class LemonadeRouterBuilder:
    def __init__(self):
        """
        Initializes the router builder targeting a Qwen3-Coder local engine 
        running on top of the AMD ROCm software platform infrastructure.
        """
        # Connects directly to the ROCm-accelerated vLLM / SGLang local endpoint
        self.api_url = os.getenv("ROCM_ENGINE_URL", "http://localhost:8000/v1")
        self.client = OpenAI(api_key="EMPTY-ROCM-POOL", base_url=self.api_url)
        
        # Target identifier matching your local container model allocation
        self.model_name = "Qwen3-Coder-30B-A3B-Instruct"
        self.tools: List[Dict[str, Any]] = []
        self.tool_registry: Dict[str, Callable] = {}

    def register_tool(self, name: str, description: str, parameters: dict, func: Callable):
        """
        Registers structural software modules that the agent can route instructions to.
        """
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

    def route_and_execute(self, user_prompt: str, temperature: float = 0.7) -> dict:
        """
        Executes intent routing with GPU acceleration via HIP-optimized engine layers.
        """
        messages = [
            {
                "role": "system", 
                "content": "You are a precise enterprise router agent. Evaluate input instructions and dispatch them to the correct function tool matching the objective."
            },
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            # Leveraging structural tool-calling capabilities optimized on Qwen3-Coder weights
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=self.tools if self.tools else None,
                tool_choice="auto" if self.tools else None,
                temperature=temperature,
                top_p=0.85
            )
            
            response_message = response.choices[0].message
            
            # Check for structured tool routing calls triggered by the model
            if response_message.tool_calls:
                execution_logs = []
                for tool_call in response_message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)
                    
                    if func_name in self.tool_registry:
                        # Direct route dispatch execution
                        runtime_output = self.tool_registry[func_name](**func_args)
                        execution_logs.append(f"[Route Target: {func_name}] Executed successfully. Output: {runtime_output}")
                    else:
                        execution_logs.append(f"[Route Error] Tool '{func_name}' found in weights path but missing in application registry.")
                
                return {"status": "success", "result": "\n".join(execution_logs)}
            
            # Text fallback mode if no structural routes match the input criteria
            return {"status": "success", "result": f"[Direct Fallback Route] {response_message.content}"}
            
        except Exception as e:
            return {"status": "error", "result": f"[Kernel/API Connection Error] Routing phase failed: {str(e)}"}

# --- Verification & Application Bridge Testing ---
if __name__ == "__main__":
    # Mock system commands to verify infrastructure routing
    def execute_hip_compilation(kernel_name: str):
        return f"ROCm compiler (hipcc) compiled kernel path: '{kernel_name}.hip.cpp' matching hardware target."

    def profile_gpu_metrics(device_id: int):
        return f"rocm-smi metrics gathered for Device [{device_id}]. Matrix operations balanced across CDNA/RDNA layout."

    # Instantiate the engine
    router = LemonadeRouterBuilder()
    
    # Register core pipeline capabilities
    router.register_tool(
        name="hip_compile",
        description="Compile standard HIP source code codebases to executable GPU binaries",
        parameters={
            "type": "object",
            "properties": {"kernel_name": {"type": "string"}},
            "required": ["kernel_name"]
        },
        func=execute_hip_compilation
    )
    
    router.register_tool(
        name="profile_hardware",
        description="Query system state, memory allocation, and active execution loops via rocm-smi",
        parameters={
            "type": "object",
            "properties": {"device_id": {"type": "integer"}},
            "required": ["device_id"]
        },
        func=profile_gpu_metrics
    )

    # Test execution
    test_run = router.route_and_execute("Check performance configurations and profile metrics for device 0 immediately.")
    print(test_run["result"])
