import ipywidgets as widgets
from IPython.display import display, clear_output
from chatbot_backend import create_initial_conversation, get_sampling_params, generate_response

# ---------------------------------------------------------------------
# UI ELEMENT SETUP
# ---------------------------------------------------------------------
message_box = widgets.Textarea(
    placeholder='Type your message here...',
    description='Message:',
    layout=widgets.Layout(width='100%', height='80px')
)

temperature_slider = widgets.FloatSlider(
    value=0.7, min=0.1, max=1.0, step=0.1,
    description='Temperature:',
    style={'description_width': '15px'}
)

max_tokens_slider = widgets.IntSlider(
    value=200, min=50, max=500, step=10,
    description='Max Tokens:',
    style={'description_width': '15px'}
)

top_p_slider = widgets.FloatSlider(
    value=0.9, min=0.1, max=1.0, step=0.1,
    description='Top P:',
    style={'description_width': '15px'}
)

send_button = widgets.Button(
    description='Send',
    button_style='success',
    icon='paper-plane'
)

output_area = widgets.Output()

# Global chat state wrapper logic 
chat_history = create_initial_conversation()

# ---------------------------------------------------------------------
# BUTTON CLICK EVENT TRIGGER
# ---------------------------------------------------------------------
def on_send_clicked(b):
    global chat_history
    user_text = message_box.value.strip()
    
    if not user_text:
        return
        
    with output_area:
        # Append User Input
        chat_history.append({"role": "user", "content": user_text})
        print(f"You: {user_text}")
        
        # Clear textbox immediately for fluid workflow feel
        message_box.value = ""
        
        # Dynamically sample dynamic UI adjustments made on dashboard parameters
        current_params = get_sampling_params(
            temperature=temperature_slider.value,
            max_tokens=max_tokens_slider.value,
            top_p=top_p_slider.value
        )
        
        print("Bot is typing...")
        try:
            # Process backend response logic pipeline
            bot_reply = generate_response(chat_history, current_params)
            
            # Repaint output context clearly without cluttering view window
            clear_output(wait=True)
            
            # Re-render conversation log clean view output
            for msg in chat_history:
                if msg["role"] == "user":
                    print(f"You: {msg['content']}")
                elif msg["role"] == "assistant":
                    print(f"Bot: {msg['content']}\n")
            
            # Print latest answer block layout elements explicitly
            print(f"Bot: {bot_reply}\n")
            
            # Cache conversation history array safely tracking context loops
            chat_history.append({"role": "assistant", "content": bot_reply})
            
        except Exception as e:
            print(f"\n[Error processing inference step request]: {e}")

# Wire click handler logic connection routine pipeline setup rules
send_button.on_click(on_send_clicked)

# Render widget dashboard suite natively within interface viewport block
display(
    widgets.VBox([
        widgets.HBox([temperature_slider, max_tokens_slider, top_p_slider]),
        message_box, 
        send_button, 
        output_area
    ])
)
