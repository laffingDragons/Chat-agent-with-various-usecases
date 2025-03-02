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
        }
        .input-container {
            display: flex;
            align-items: center;
            gap: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Force user to enter API Key before accessing UI
if "openai_api_key" not in st.session_state or not st.session_state["openai_api_key"]:
    st.session_state["openai_api_key"] = st.text_input(
        "Enter your OpenAI API Key (for GPT-4 or GPT-3.5 Turbo)",
        type="password"
    )
    if st.session_state["openai_api_key"]:
        st.success("API Key Saved! Please refresh if UI is not enabled.")
        st.rerun()
    else:
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
    response = openai.ChatCompletion.create(
        model="gpt-4",
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

# Define different pastel colors for cards
pastel_colors = ["#FFC3A0", "#B5EAD7", "#FFDAC1", "#C7CEEA", "#FF9AA2", "#FFB7B2", "#E2F0CB", "#B4A7D6"]

# UI Layout
st.title("AI Use Cases Dashboard")

st.markdown("""<div class='card-container'>""", unsafe_allow_html=True)

cols = st.columns(4)

for idx, use_case in enumerate(use_cases):
    with cols[idx % 4]:
        st.markdown(f"""<div class='card' style='background-color:{pastel_colors[idx % len(pastel_colors)]};' onclick='document.getElementById("btn_{idx}").click();'>{use_case}</div>""", unsafe_allow_html=True)
        if st.button(use_case, key=f"btn_{idx}", help="Click to open chat"):
            st.session_state["active_use_case"] = use_case
            st.session_state["show_modal"] = True

st.markdown("""</div>""", unsafe_allow_html=True)

# Modal Chat Window
if "show_modal" in st.session_state and st.session_state["show_modal"]:
    st.markdown("""<div class='chat-modal'>""", unsafe_allow_html=True)
    st.subheader(st.session_state["active_use_case"])
    with st.container():
        col1, col2 = st.columns([4, 1])
        user_input = col1.text_input("Enter your query:", key="user_input")
        send_button = col2.button("Send")
    if send_button:
        response = chat_with_ai(user_input, use_memory=(st.session_state["active_use_case"] == "Chat Agent with Memory / Context of Previous Conversation"))
        st.text_area("AI Response:", response, height=200)
    if st.button("Close"):
        st.session_state["show_modal"] = False
    st.markdown("""</div>""", unsafe_allow_html=True)
