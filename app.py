import streamlit as st
import openai
from openai import OpenAI
import json

# Set Streamlit Page Config
st.set_page_config(page_title="AI Use Cases Dashboard", layout="wide")

# Custom Styling for Mobile & Desktop
st.markdown(
    """
    <style>
        body {
            background-color: #F8F9FA;
        }
        .card-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
            padding: 15px;
        }
        .chat-modal {
            background-color: #FFFFFF;
            border-radius: 15px;
            padding: 15px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            width: 90%;
            max-width: 600px;
            margin: 0 auto;
        }
        .input-container {
            display: flex;
            flex-direction: row;
            align-items: center;
            gap: 10px;
        }
        @media (max-width: 768px) {
            .card-container {
                flex-direction: column;
                align-items: center;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state variables
if "openai_api_key" not in st.session_state:
    st.session_state["openai_api_key"] = st.query_params.get("api_key", [""])[0]

if "chat_memory" not in st.session_state:
    st.session_state["chat_memory"] = []

if "active_use_case" not in st.session_state:
    st.session_state["active_use_case"] = None

if "show_modal" not in st.session_state:
    st.session_state["show_modal"] = False

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Function to validate API key
def validate_and_store_api_key(api_key):
    """Validates the API key and stores it in session state if valid."""
    try:
        client = OpenAI(api_key=api_key)
        response = client.models.list()
        if response:
            st.session_state["openai_api_key"] = api_key
            st.query_params["api_key"] = api_key
            st.success("API Key validated and saved successfully!")
            return True
    except Exception as e:
        st.error(f"API Key validation failed: {str(e)}")
        return False

# Collapsible API Key Section
with st.expander("🔑 Edit API Key"):
    api_key_input = st.text_input("OpenAI API Key", type="password", value=st.session_state["openai_api_key"])
    if st.button("Save API Key"):
        if validate_and_store_api_key(api_key_input):
            st.rerun()

# Check for API key before proceeding
if not st.session_state["openai_api_key"]:
    st.warning("Please enter your OpenAI API Key to proceed!")
    st.stop()

# Function to interact with OpenAI API
def chat_with_ai(prompt, use_case, use_memory=False):
    try:
        client = OpenAI(api_key=st.session_state["openai_api_key"])
        
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
        
        # Make API call
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        
        reply = response.choices[0].message.content
        
        # Update chat memory if using memory
        if use_memory:
            # Only store the last few messages to prevent context length issues
            if len(st.session_state["chat_memory"]) > 8:  # Keep last 4 exchanges (8 messages)
                st.session_state["chat_memory"] = st.session_state["chat_memory"][-8:]
            
            st.session_state["chat_memory"].append({"role": "user", "content": prompt})
            st.session_state["chat_memory"].append({"role": "assistant", "content": reply})
        
        return reply
        
    except Exception as e:
        return f"Error: {str(e)}"

# Function to handle use case selection
def select_use_case(use_case):
    st.session_state["active_use_case"] = use_case
    st.session_state["show_modal"] = True
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

pastel_colors = ["#FFB6C1", "#FFD700", "#87CEEB", "#98FB98", "#FF69B4", "#FFA07A", "#D8BFD8", "#F0E68C"]

# UI Layout
st.title("AI Use Cases Dashboard")

# Create a grid layout for the use case buttons
cols = st.columns(4)
for idx, use_case in enumerate(use_cases):
    with cols[idx % 4]:
        if st.button(use_case, key=f"btn_{idx}", use_container_width=True, 
                    help="Click to open chat",
                    type="primary" if st.session_state["active_use_case"] == use_case else "secondary"):
            select_use_case(use_case)
            st.rerun()

# Chat modal
if st.session_state["show_modal"] and st.session_state["active_use_case"]:
    st.markdown("---")
    st.subheader(f"Chat: {st.session_state['active_use_case']}")
    
    # Display chat history
    for message in st.session_state["chat_history"]:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**AI:** {message['content']}")
    
    # Chat input
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_area("Your message:", key="user_input", height=100)
        submit_button = st.form_submit_button("Send")
        
        if submit_button and user_input.strip():
            # Determine if this use case uses memory
            use_memory = "with Memory" in st.session_state["active_use_case"]
            
            # Get AI response
            response = chat_with_ai(user_input, st.session_state["active_use_case"], use_memory)
            
            # Update chat history
            st.session_state["chat_history"].append({"role": "user", "content": user_input})
            st.session_state["chat_history"].append({"role": "assistant", "content": response})
            
            st.rerun()
    
    # Add a button to close the chat modal
    if st.button("Close Chat", type="secondary"):
        st.session_state["show_modal"] = False
        st.rerun()
