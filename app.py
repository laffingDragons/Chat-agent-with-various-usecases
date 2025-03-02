import streamlit as st
import openai
import json

# Set Streamlit Page Config
st.set_page_config(page_title="AI Use Cases", layout="wide")

# Custom Styling
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
            gap: 20px;
            padding: 20px;
        }
        .card {
            width: 300px;
            height: 200px;
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            font-size: 18px;
            font-weight: bold;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            cursor: pointer;
        }
        .chat-modal {
            background-color: #FFFFFF;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            width: 600px;
            max-width: 90%;
            position: relative;
        }
        .input-container {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .close-button {
            position: absolute;
            top: 10px;
            right: 10px;
            cursor: pointer;
            font-size: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Check if API Key exists in local storage
if "openai_api_key" not in st.session_state:
    st.session_state["openai_api_key"] = st.query_params.get("api_key", [""])[0]

def validate_and_store_api_key(api_key):
    """Validates the API key and stores it in local storage if valid."""
    openai.api_key = api_key
    try:
        response = openai.models.list()
        if response:
            st.session_state["openai_api_key"] = api_key
            st.query_params["api_key"] = api_key  # Store key in local storage
            st.success("API Key validated and saved successfully!")
            st.rerun()
    except openai.error.AuthenticationError:
        st.error("Invalid API Key! Please enter a valid one.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

# Ask for API key only if not already stored
if not st.session_state["openai_api_key"]:
    api_key_input = st.text_input(
        "Enter your OpenAI API Key (for GPT-4 or GPT-3.5 Turbo)",
        type="password"
    )
    if st.button("Save API Key"):
        validate_and_store_api_key(api_key_input)
    st.stop()

# Function to interact with OpenAI API
def chat_with_ai(prompt, use_memory=False):
    openai.api_key = st.session_state["openai_api_key"]
    if not openai.api_key:
        return "Error: API Key is required!"
    
    memory = []
    if use_memory and "chat_memory" in st.session_state:
        memory = st.session_state["chat_memory"]
    
    messages = memory + [{"role": "user", "content": prompt}]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages
        )
        reply = response["choices"][0]["message"]["content"]
    except openai.error.AuthenticationError:
        st.error("Invalid API Key! Please update your key.")
        return "Invalid API Key"
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return "Error processing request"
    
    if use_memory:
        st.session_state["chat_memory"] = messages + [{"role": "assistant", "content": reply}]
    
    return reply

# List of Use Cases
use_cases = [
    "Story Generating AI Agent",
    "Generate a Comic Story",
    "AI Agent for Translation",
    "AI Agent for Summarization",
    "AI Agent for Image Creation",
    "AI Agent for Scenic Views",
    "Traditional Chatbot (No Feedback / No Memory / No Context of Previous Chat)",
    "Chat Agent with Memory / Context of Previous Conversation"
]

# Define different pastel colors for cards
pastel_colors = ["#FFC3A0", "#B5EAD7", "#FFDAC1", "#C7CEEA", "#FF9AA2", "#FFB7B2", "#E2F0CB", "#B4A7D6"]

# UI Layout
st.title("AI Use Cases Dashboard")

st.markdown("""<div class='card-container'>""", unsafe_allow_html=True)

cols = st.columns(4)

for idx, use_case in enumerate(use_cases):
    with cols[idx % 4]:
        if st.button(use_case, key=f"btn_{idx}", help="Click to open chat"):
            st.session_state["active_use_case"] = use_case
            st.session_state["show_modal"] = True

st.markdown("""</div>""", unsafe_allow_html=True)

# Modal Chat Window
if "show_modal" in st.session_state and st.session_state["show_modal"]:
    st.markdown("""<div class='chat-modal'>""", unsafe_allow_html=True)
    st.markdown("<span class='close-button' onclick='window.location.reload()'>✖</span>", unsafe_allow_html=True)
    st.subheader(st.session_state["active_use_case"])
    with st.container():
        col1, col2 = st.columns([4, 1])
        user_input = col1.text_input("Enter your query:", key="user_input")
        send_button = col2.button("Send")
    if send_button:
        response = chat_with_ai(user_input, use_memory=(st.session_state["active_use_case"] == "Chat Agent with Memory / Context of Previous Conversation"))
        st.text_area("AI Response:", response, height=200)
    st.markdown("""</div>""", unsafe_allow_html=True)
