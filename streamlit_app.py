from dataclasses import dataclass
from typing import Literal
import streamlit as st
from langchain.chains.conversation.memory import ConversationSummaryMemory
import streamlit.components.v1 as components
from openai import OpenAI

@dataclass
class Message:
    """Class for keeping track of a chat message."""
    origin: Literal["human", "ai"]
    message: str

def load_css():
    with open("static/styles.css", "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

def initialize_session_state():
    if "history" not in st.session_state:
        st.session_state.history = []
    if "token_count" not in st.session_state:
        st.session_state.token_count = 0
    if "conversation" not in st.session_state:
        # You don't need to initialize an OpenAI model anymore as we are switching to Gemini.
        st.session_state.conversation = None

def on_click_callback():
    # Call the chatbot function using the user's input
    human_prompt = st.session_state.human_prompt
    llm_response = chatbot_function(human_prompt)
    
    print(llm_response)
    st.session_state.history.append(
        Message("human", human_prompt)
    )
    st.session_state.history.append(
        Message("ai", llm_response)
    )
    st.session_state.human_prompt = ""

def chatbot_function(user_input):

    client = OpenAI(
        api_key=st.secrets["GEMINI_API_KEY"],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    response = client.chat.completions.create(
        model="gemini-2.0-flash",
        n=1,
        messages=[
            {"role": "system", "content": "You are an AI chatbot specialized in assisting with research-related inquiries, providing accurate, well-cited, and in-depth responses. You offer insights into academic research, literature reviews, methodologies, AI/ML trends, and technical implementations. You guide users in writing research papers, structuring content, and ensuring ethical standards like proper citation and avoiding plagiarism. You provide programming assistance for AI and data science while encouraging best research practices such as reproducibility and peer review. When discussing recent research, you suggest reliable sources like Google Scholar, arXiv, and IEEE Xplore. You engage users by recommending relevant journals, conferences, and step-by-step research guidance. You must response Not in Html or Markdown."},
            {
                "role": "user",
                "content": user_input
            }
        ]
    )
    res = response.choices[0].message.content
    return res


load_css()
initialize_session_state()

st.title("Research Chatbot 🤖")

chat_placeholder = st.container()
prompt_placeholder = st.form("chat-form")
credit_card_placeholder = st.empty()

with chat_placeholder:
    for chat in st.session_state.history:
        div = f"""
    <div class="chat-row {'' if chat.origin == 'ai' else 'row-reverse'}">
        <img class="chat-icon" src="app/static/{'ai_icon.png' if chat.origin == 'ai' else 'user_icon.png'}" width=32 height=32>
        <div class="chat-bubble {'ai-bubble' if chat.origin == 'ai' else 'human-bubble'}">{chat.message}</div>
    </div>
    """
        st.markdown(div, unsafe_allow_html=True)
    for _ in range(3):
        st.markdown("")  # Empty rows for spacing

with prompt_placeholder:
    st.markdown("**Chat**")
    cols = st.columns((6, 1))
    cols[0].text_input(
        "Chat",
        value="Hello bot",
        label_visibility="collapsed",
        key="human_prompt",
    )
    cols[1].form_submit_button(
        "Submit", 
        type="primary", 
        on_click=on_click_callback, 
    )

credit_card_placeholder.caption(f"""
Used {st.session_state.token_count} tokens \n
Debug Langchain conversation: 
{st.session_state.conversation.memory.buffer if st.session_state.conversation else 'No conversation yet.'}
""")

components.html("""
<script>
const streamlitDoc = window.parent.document;

const buttons = Array.from(
    streamlitDoc.querySelectorAll('.stButton > button')
);
const submitButton = buttons.find(
    el => el.innerText === 'Submit'
);

streamlitDoc.addEventListener('keydown', function(e) {
    switch (e.key) {
        case 'Enter':
            submitButton.click();
            break;
    }
});
</script>
""", 
    height=0,
    width=0,
)
