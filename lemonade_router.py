import json
from typing import Callable, Dict, List, Any
from openai import OpenAI

class LemonadeRouterBuilder:
    def __init__(self, api_key: str = "ollama/lemonade", base_url: str = "http://localhost:11434/v1"):
        """
        Initializes the router builder targeting Qwen3-Coder-30B-A3B-Instruct.
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        # Using the standard model tag for local deployment instances
        self.model_name = "mdq100/Qwen3-Coder-30B-A3B-Instruct:30b"
        self.tools: List[Dict[str, Any]] = []
        self.tool_registry: Dict[str, Callable] = {}

    def register_tool(self, name: str, description: str, parameters: dict, func: Callable):
        """
        Registers a function tool that the router can invoke dynamically.
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

    def route_and_execute(self, user_prompt: str) -> str:
        """
        Routes the user intent to the correct function or direct text output.
        """
        messages = [{"role": "user", "content": user_prompt}]
        
        # Qwen3-Coder excels at tool calling with 0.7 temperature configurations
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            tools=self.tools if self.tools else None,
            tool_choice="auto" if self.tools else None,
            temperature=0.7,
            top_p=0.8
        )
        
        response_message = response.choices[0].message
        
        # Check if the model decided to route execution to a tool
        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name in self.tool_registry:
                    # Execute the matched route function
                    route_output = self.tool_registry[function_name](**function_args)
                    return f"[Route Executed: {function_name}] Output: {route_output}"
                
        return f"[Direct Fallback Route] Response: {response_message.content}"

# --- Example Usage ---
if __name__ == "__main__":
    # Define placeholder mock services to route between
    def get_code_syntax_checker(repo_path: str):
        return f"Repository '{repo_path}' passed Qwen3 lint checks."

    def deploy_to_production(environment: str):
        return f"Successfully routed code artifact to {environment} layer."

    # Initialize router builder
    router = LemonadeRouterBuilder()

    # Register routes with schemas
    router.register_tool(
        name="verify_repository",
        description="Run linting and syntax validations on local codebases",
        parameters={
            "type": "object",
            "properties": {"repo_path": {"type": "string"}},
            "required": ["repo_path"]
        },
        func=get_code_syntax_checker
    )

    router.register_tool(
        name="trigger_deployment",
        description="Deploy software modifications to staging or production targets",
        parameters={
            "type": "object",
            "properties": {"environment": {"type": "string"}},
            "required": ["environment"]
        },
        func=deploy_to_production
    )

    # Test the agentic routing capabilities
    test_prompt = "Everything looks clean, please trigger a deployment to production right now."
    print("Routing instruction...")
    result = router.route_and_execute(test_prompt)
    print(result)
