# =====================================================================
# 1. LOAD THE MODEL
# =====================================================================
print("Loading model 'Qwen/Qwen3-4B-Instruct-2507' on AMD MI300 GPU...")
from vllm import LLM, SamplingParams

# Load the AI model onto the MI300 GPU (takes about a minute)
model_name = "Qwen/Qwen3-4B-Instruct-2507"
llm = LLM(model=model_name)
print("Model loaded and ready!")

# =====================================================================
# 2. DEFINE SYSTEM PROMPTS & PARAMETERS
# =====================================================================
# Example custom prompts from the lab guidelines:
# - Shakespeare Bot: "You are a chatbot that speaks like William Shakespeare."
# - Pirate Bot: "You are a friendly pirate. Talk like a pirate!"
# - Rap Bot: "You are a talented rapper. Respond only in rhymes and rap lyrics."
# - Cat Bot: "You are a cat. Respond with meows."

SYSTEM_PROMPT = "You are a friendly pirate. Talk like a pirate!"

def create_initial_conversation(system_instruction=SYSTEM_PROMPT):
    """Initializes the conversation list with a system role layout."""
    return [
        {"role": "system", "content": system_instruction}
    ]

def get_sampling_params(temperature=0.7, max_tokens=200, top_p=0.9):
    """
    Configures sampling parameters:
    - temperature: 0.1-0.3 (factual), 0.5-0.7 (chat), 0.8-1.0 (creative)
    - max_tokens: 50-100 (short), 150-300 (medium), 500+ (long)
    - top_p: 0.1-0.5 (conservative), 0.7-0.9 (balanced), 0.95-1.0 (diverse)
    """
    return SamplingParams(
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p
    )

# =====================================================================
# 3. CORE INFERENCE FUNCTION
# =====================================================================
def generate_response(conversation_history, sampling_params):
    """Sends the ongoing chat log history straight to vLLM engine."""
    outputs = llm.chat(conversation_history, sampling_params)
    # Extract structural text output layer safely
    bot_message = outputs[0].outputs[0].text
    return bot_message
