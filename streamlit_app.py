# -----------------------------
# IMPORTING LIBRARIES
# -----------------------------
import streamlit as st
import requests

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="RAG Chatbot",
    layout="centered"
)

# -----------------------------
# CUSTOM CSS
# -----------------------------
st.markdown("""
<style>

.main {
    background-color: #0E1117;
    color: white;
}

.stChatMessage {
    border-radius: 10px;
    padding: 10px;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# SESSION STATE
# -----------------------------
if "messages" not in st.session_state:

    st.session_state.messages = []

# -----------------------------
# OLLAMA FUNCTION
# -----------------------------
def generate_answer(query):

    prompt = f"""
You are a helpful AI assistant.

Give a short, accurate, and clear answer.
Do not provide incorrect information.
Keep the response under 5 sentences.

Question:
{query}
"""

    response = requests.post(

        "http://localhost:11434/api/generate",

        json={

            "model": "tinyllama",

            "prompt": prompt,

            "stream": False,

            "options": {
                "num_predict": 80
            }
        }
    )

    return response.json()["response"]

# -----------------------------
# CENTER TITLE
# -----------------------------
st.markdown("""

<h1 style='
text-align: center;
color: white;
font-size: 55px;
margin-top: 40px;
'>
RAG CHATBOT
</h1>

<p style='
text-align: center;
color: #BBBBBB;
font-size: 20px;
margin-bottom: 40px;
'>
Ask anything about Artificial Intelligence.
</p>

""", unsafe_allow_html=True)

# -----------------------------
# DISPLAY OLD CHATS
# -----------------------------
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])

# -----------------------------
# CHAT INPUT
# -----------------------------
query = st.chat_input(
    "Ask your question"
)

if query:

    # -------------------------
    # SAVE USER MESSAGE
    # -------------------------
    st.session_state.messages.append(
        {
            "role": "user",
            "content": query
        }
    )

    # -------------------------
    # SHOW USER MESSAGE
    # -------------------------
    with st.chat_message("user"):

        st.write(query)

    # -------------------------
    # GENERATE ANSWER
    # -------------------------
    with st.chat_message("assistant"):

        with st.spinner(
            "Generating answer..."
        ):

            answer = generate_answer(query)

            st.write(answer)

    # -------------------------
    # SAVE ASSISTANT MESSAGE
    # -------------------------
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )