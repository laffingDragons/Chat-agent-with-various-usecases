import streamlit as st
import openai
import requests
import json
import os
import sys

# First thing: add this environment variable to disable Pillow requirement
os.environ['STREAMLIT_IMAGE_MODE'] = 'url'

# Set Streamlit Page Config
st.set_page_config(page_title="AI Use Cases Dashboard", layout="wide")

# Custom Styling for Mobile & Desktop
st.markdown(
    """
    <style>
        .button-container {
            display: flex;
            flex-direction: column;
            width: 100%;
            margin: 10px 0;
        }
        .custom-button {
            height: 120px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 15px;
            margin: 5px 0;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            transition: transform 0.2s;
            color: black;
            border: none;
            width: 100%;
        }
        .custom-button:hover {
            transform: scale(1.05);
            box-shadow: 0px 6px 10px rgba(0, 0, 0, 0.15);
        }
        .chat-container {
            background-color: #FFFFFF;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
            margin-top: 20px;
            position: relative;
        }
        .chat-history {
            max-height: 400px;
            overflow-y: auto;
            margin-bottom: 20px;
            padding: 10px;
            border-radius: 10px;
            background-color: #F8F9FA;
        }
        .user-message {
            background-color: #DCF8C6;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
        }
        .ai-message {
            background-color: #F0F0F0;
            padding: 10px;
            border-radius: 10px;
            margin: 5px 0;
        }
        .close-icon {
            position: absolute;
            top: 10px;
            right: 10px;
            font-size: 24px;
            cursor: pointer;
            background: none;
            border: none;
            color: #555;
        }
        .img-container {
            text-align: center;
            margin: 10px 0;
        }
        .img-container img {
            max-width: 100%;
            border-radius: 10px;
        }
        @media (max-width: 768px) {
            .custom-button {
                height: 100px;
                font-size: 16px;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state variables
if "openai_api_key" not in st.session_state:
    st.session_state["openai_api_key"] = ""

if "chat_memory" not in st.session_state:
    st.session_state["chat_memory"] = []

if "active_use_case" not in st.session_state:
    st.session_state["active_use_case"] = None

if "show_chat" not in st.session_state:
    st.session_state["show_chat"] = False

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "api_key_expanded" not in st.session_state:
    st.session_state["api_key_expanded"] = True

# Function to validate API key
def validate_and_store_api_key(api_key):
    """Validates the API key and stores it in session state if valid."""
    try:
        openai.api_key = api_key
        # Try a simple request to validate the key
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        if response.status_code == 200:
            st.session_state["openai_api_key"] = api_key
            st.session_state["api_key_expanded"] = False  # Auto-collapse after successful validation
            return True
        else:
            st.error(f"API Key validation failed. Status code: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"API Key validation failed: {str(e)}")
        return False

# Collapsible API Key Section
api_key_expander = st.expander("🔑 Edit API Key", expanded=st.session_state["api_key_expanded"])
with api_key_expander:
    api_key_input = st.text_input("OpenAI API Key", type="password", value=st.session_state["openai_api_key"])
    if st.button("Save API Key"):
        if validate_and_store_api_key(api_key_input):
            st.success("API Key validated and saved successfully!")
            st.experimental_rerun()

# Check for API key before proceeding
if not st.session_state["openai_api_key"]:
    st.warning("Please enter your OpenAI API Key to proceed!")
    st.stop()

# Function to generate completion text
def generate_completion(prompt, max_tokens=3000, outputs=1):
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state['openai_api_key']}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-3.5-turbo-instruct",
            "prompt": prompt,
            "max_tokens": max_tokens,
            "n": outputs
        }
        response = requests.post(
            "https://api.openai.com/v1/completions",
            headers=headers,
            json=data
        )
        if response.status_code == 200:
            result = response.json()
            output = []
            for choice in result.get("choices", []):
                output.append(choice.get("text", "").strip())
            return output
        else:
            return [f"Error: API returned status code {response.status_code}"]
    except Exception as e:
        return [f"Error: {str(e)}"]

# Function to generate images
def generate_image(prompt, size="512x512"):
    try:
        headers = {
            "Authorization": f"Bearer {st.session_state['openai_api_key']}",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": prompt,
            "n": 1,
            "size": size
        }
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers=headers,
            json=data
        )
        if response.status_code == 200:
            result = response.json()
            return result.get("data", [{}])[0].get("url", None)
        else:
            st.error(f"Image generation failed: API returned status code {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Image generation failed: {str(e)}")
        return None

# Function to interact with OpenAI API for chat
def chat_with_ai(prompt, use_case, use_memory=False):
    try:
        # Prepare messages based on use case
        messages = []
        
        # Add system message based on use case
        if "Story Generating" in use_case:
            system_msg = "You are a creative storyteller. Create an engaging short story based on the user's input."
        elif "Comic Story" in use_case:
            system_msg = "You are a comic book writer. Create a short comic script with scenes and dialogue based on the user's input."
        elif "Translation" in use_case:
            system_msg = "You are a translator. Translate the user's text into the requested language."
        elif "Summarization" in use_case:
            system_msg = "You are a summarization expert. Provide a concise summary of the text provided by the user."
        elif "Image Creation" in use_case or "Scenic Views" in use_case:
            system_msg = "You are an image description expert. Provide a detailed description that could be used to generate an image based on the user's request."
        else:
            system_msg = "You are a helpful AI assistant."
        
        messages.append({"role": "system", "content": system_msg})
        
        # Add chat memory if using memory
        if use_memory and st.session_state["chat_memory"]:
            messages.extend(st.session_state["chat_memory"])
        
        # Add the current user message
        messages.append({"role": "user", "content": prompt})
        
        # Make API call directly without the OpenAI SDK
        headers = {
            "Authorization": f"Bearer {st.session_state['openai_api_key']}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": messages
        }
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            reply = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Update chat memory if using memory
            if use_memory:
                # Only store the last few messages to prevent context length issues
                if len(st.session_state["chat_memory"]) > 8:  # Keep last 4 exchanges (8 messages)
                    st.session_state["chat_memory"] = st.session_state["chat_memory"][-8:]
                
                st.session_state["chat_memory"].append({"role": "user", "content": prompt})
                st.session_state["chat_memory"].append({"role": "assistant", "content": reply})
            
            return reply
        else:
            return f"Error: API returned status code {response.status_code}"
            
    except Exception as e:
        return f"Error: {str(e)}"

# Function to handle use case selection
def select_use_case(use_case):
    st.session_state["active_use_case"] = use_case
    st.session_state["show_chat"] = True
    if "Memory" not in use_case:
        st.session_state["chat_memory"] = []  # Reset memory on new use case
    st.session_state["chat_history"] = []  # Reset chat history

# List of Use Cases with Different Colors
use_cases = [
    "Story Generating AI Agent",
    "Generate a Comic Story",
    "AI Agent for Translation",
    "AI Agent for Summarization",
    "AI Agent for Image Creation",
    "AI Agent for Scenic Views",
    "Traditional Chatbot (No Memory)",
    "Chat Agent with Memory"
]

button_colors = [
    "#FFB6C1",  # Light Pink
    "#FFD700",  # Gold
    "#87CEEB",  # Sky Blue
    "#98FB98",  # Pale Green
    "#FF69B4",  # Hot Pink
    "#FFA07A",  # Light Salmon
    "#D8BFD8",  # Thistle
    "#F0E68C"   # Khaki
]

# UI Layout
st.title("AI Use Cases Dashboard")

# Create a grid layout for the use case buttons
cols = st.columns(4)
for idx, use_case in enumerate(use_cases):
    color = button_colors[idx % len(button_colors)]
    with cols[idx % 4]:
        if st.button(
            use_case, 
            key=f"btn_{idx}",
            on_click=select_use_case,
            args=(use_case,),
            help=f"Start chatting with {use_case}"
        ):
            pass

# Chat interface
if st.session_state["show_chat"] and st.session_state["active_use_case"]:
    st.markdown("---")
    
    # Chat header with close button
    col1, col2 = st.columns([0.95, 0.05])
    with col1:
        st.subheader(st.session_state['active_use_case'])
    with col2:
        if st.button("✖", key="close_button", help="Close chat"):
            st.session_state["show_chat"] = False
            st.experimental_rerun()
    
    # Display chat history
    if st.session_state["chat_history"]:
        chat_history_html = '<div class="chat-history">'
        for message in st.session_state["chat_history"]:
            if message["role"] == "user":
                chat_history_html += f'<div class="user-message"><strong>You:</strong> {message["content"]}</div>'
            elif message["role"] == "assistant":
                if message.get("is_image", False):
                    chat_history_html += f'<div class="ai-message"><strong>AI:</strong> Generated image:</div>'
                    chat_history_html += f'<div class="img-container"><a href="{message["content"]}" target="_blank"><img src="{message["content"]}" alt="Generated image"></a></div>'
                else:
                    chat_history_html += f'<div class="ai-message"><strong>AI:</strong> {message["content"]}</div>'
        chat_history_html += '</div>'
        st.markdown(chat_history_html, unsafe_allow_html=True)
    
    # Chat input
    active_use_case = st.session_state["active_use_case"]
    
    # Different input prompts based on use case
    if "Image Creation" in active_use_case or "Scenic Views" in active_use_case:
        placeholder_text = "Describe the image you want to generate..."
    elif "Translation" in active_use_case:
        placeholder_text = "Enter text to translate and the target language..."
    elif "Summarization" in active_use_case:
        placeholder_text = "Enter text to summarize..."
    elif "Story" in active_use_case:
        placeholder_text = "Enter a prompt for your story..."
    else:
        placeholder_text = "Type your message here..."
    
    user_input = st.text_area("Your message:", placeholder=placeholder_text, key="user_input", height=100)
    if st.button("Send", key="send_button"):
        if user_input.strip():
            # Handle different use cases
            is_memory_enabled = "Memory" in active_use_case and "No Memory" not in active_use_case
            
            # Add user input to chat history
            st.session_state["chat_history"].append({"role": "user", "content": user_input})
            
            # Handle image generation use cases
            if "Image Creation" in active_use_case or "Scenic Views" in active_use_case:
                image_url = generate_image(user_input)
                if image_url:
                    st.session_state["chat_history"].append({
                        "role": "assistant", 
                        "content": image_url,
                        "is_image": True
                    })
            # Handle text-based use cases
            else:
                if "Story Generating" in active_use_case:
                    # Use completion API for story generation
                    response = generate_completion(f"Write a short story about: {user_input}")[0]
                elif "Comic Story" in active_use_case:
                    # Use completion API for comic story generation
                    response = generate_completion(f"Write a short comic script about: {user_input}")[0]
                else:
                    # Use chat API for other use cases
                    response = chat_with_ai(user_input, active_use_case, is_memory_enabled)
                
                st.session_state["chat_history"].append({
                    "role": "assistant", 
                    "content": response
                })
            
            st.experimental_rerun()

# Add information at the bottom
st.markdown("---")
st.markdown("### How to use this dashboard")
st.markdown("""
1. Enter your OpenAI API key in the 'Edit API Key' section
2. Click on any use case button to start interacting with that specific AI agent
3. Enter your prompt in the text area and click 'Send'
4. For image generation use cases, describe the image you want to create
5. For the Memory-enabled chatbot, your conversation history will be maintained
""")
