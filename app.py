import streamlit as st
import openai
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
            position: relative;
        }
        .input-container {
            display: flex;
            flex-direction: row;
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

# API Key Handling with Edit Option
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

# Collapsible API Key Section
with st.expander("🔑 Edit API Key"):
    api_key_input = st.text_input("Update OpenAI API Key", type="password", value=st.session_state["openai_api_key"])
    if st.button("Save API Key"):
        validate_and_store_api_key(api_key_input)

if not st.session_state["openai_api_key"]:
    st.warning("API Key is required to proceed!")
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
        response = openai.client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        reply = response.choices[0].message.content
    except openai.AuthenticationError:
        st.error("Invalid API Key! Please update your key.")
        return "Invalid API Key"
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return "Error processing request"
    
    if use_memory:
        st.session_state["chat_memory"] = messages + [{"role": "assistant", "content": reply}]
    
    return reply

# List of Use Cases with Different Colors
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

pastel_colors = ["#FFB6C1", "#FFD700", "#87CEEB", "#98FB98", "#FF69B4", "#FFA07A", "#D8BFD8", "#F0E68C"]

# UI Layout
st.title("AI Use Cases Dashboard")

st.markdown("""<div class='card-container'>""", unsafe_allow_html=True)

cols = st.columns(4)

for idx, use_case in enumerate(use_cases):
    with cols[idx % 4]:
        st.markdown(f"""
            <button style='width:100%; height:80px; background-color:{pastel_colors[idx % len(pastel_colors)]};
            border:none; border-radius:10px; font-size:16px; font-weight:bold; cursor:pointer;' 
            onclick='window.location.reload()'>
                {use_case}
            </button>
        """, unsafe_allow_html=True)
        if st.button(use_case, key=f"btn_{idx}", help="Click to open chat"):
            st.session_state["active_use_case"] = use_case
            st.session_state["show_modal"] = True

st.markdown("""</div>""", unsafe_allow_html=True)

# Modal Chat Window
if "show_modal" in st.session_state and st.session_state["show_modal"]:
    st.markdown("""<div class='chat-modal'>""", unsafe_allow_html=True)
    if st.button("✖", key="close_modal"):
        st.session_state["show_modal"] = False
        st.rerun()
    st.subheader(st.session_state["active_use_case"])
    user_input = st.text_input("", key="user_input")
    if st.button("Send"):
        response = chat_with_ai(user_input, use_memory=(st.session_state["active_use_case"] == "Chat Agent with Memory / Context of Previous Conversation"))
        st.text_area("AI Response:", response, height=200)
    st.markdown("""</div>""", unsafe_allow_html=True)
