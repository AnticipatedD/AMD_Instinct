import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def initialize_native_router_pipeline():
    """
    Direct loading pipeline for unsloth/Qwen3-Coder-30B-A3B-Instruct native weights.
    """
    model_id = "unsloth/Qwen3-Coder-30B-A3B-Instruct"
    
    print(f"Pulling model weights and tokenizer configurations for {model_id}...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    
    # Utilizing device_map auto for proper memory layers across active MoE routing
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto"
    )
    
    # Constructing a tool framework natively via chat templates
    messages = [
        {"role": "system", "content": "You are the primary orchestration system routing intents between system services."},
        {"role": "user", "content": "Check code structure for /home/workspace."}
    ]
    
    # Applying the specialized Qwen3 chat template structure
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)
    
    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=512,
        temperature=0.7,
        top_p=0.8
    )
    
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response

if __name__ == "__main__":
    # To run local inference natively via transformers weights uncomment below:
    # print(initialize_native_router_pipeline())
    pass
