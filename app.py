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
        .card {
            background-color: #FFFFFF;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            text-align: center;
        }
        .chat-modal {
            background-color: #FFFFFF;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            width: 600px;
            max-width: 90%;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Store API Key in Local Storage
if "openai_api_key" not in st.session_state:
    st.session_state["openai_api_key"] = ""

def save_api_key():
    st.session_state["openai_api_key"] = st.text_input(
        "Enter your OpenAI API Key (for GPT-3.5 Turbo)",
        value=st.session_state["openai_api_key"],
        type="password"
    )
    if st.session_state["openai_api_key"]:
        st.success("API Key Saved!")

save_api_key()

# Function to interact with OpenAI API
def chat_with_ai(prompt, use_memory=False):
    openai.api_key = st.session_state["openai_api_key"]
    if not openai.api_key:
        return "Error: API Key is required!"
    
    memory = []
    if use_memory and "chat_memory" in st.session_state:
        memory = st.session_state["chat_memory"]
    
    messages = memory + [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    
    reply = response["choices"][0]["message"]["content"]
    
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

# UI Layout
st.title("AI Use Cases Dashboard")

cols = st.columns(4)

for idx, use_case in enumerate(use_cases):
    with cols[idx % 4]:
        if st.button(use_case, key=f"btn_{idx}"):
            st.session_state["active_use_case"] = use_case
            st.session_state["show_modal"] = True

# Modal Chat Window
if "show_modal" in st.session_state and st.session_state["show_modal"]:
    st.markdown("""<div class='chat-modal'>""", unsafe_allow_html=True)
    st.subheader(st.session_state["active_use_case"])
    user_input = st.text_input("Enter your query:")
    if st.button("Send"):
        response = chat_with_ai(user_input, use_memory=(st.session_state["active_use_case"] == "Chat Agent with Memory / Context of Previous Conversation"))
        st.text_area("AI Response:", response, height=200)
    if st.button("Close"):
        st.session_state["show_modal"] = False
    st.markdown("""</div>""", unsafe_allow_html=True)
