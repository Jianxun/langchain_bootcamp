import streamlit as st
from day1_simple_chatbot import create_chatbot
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_style" not in st.session_state:
    st.session_state.current_style = "basic"
if "chatbot" not in st.session_state:
    st.session_state.chatbot = create_chatbot(style=st.session_state.current_style)

# Set page config
st.set_page_config(
    page_title="LangChain Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Title and description
st.title("🤖 LangChain Chatbot")
st.markdown("""
This is a simple chatbot built with LangChain and Streamlit. 
You can switch between different conversation styles using the dropdown menu below.
""")

# Style selector
styles = ["basic", "detailed", "friendly", "professional"]
selected_style = st.selectbox(
    "Select Conversation Style",
    styles,
    index=styles.index(st.session_state.current_style)
)

# Update chatbot if style changes
if selected_style != st.session_state.current_style:
    st.session_state.current_style = selected_style
    st.session_state.chatbot = create_chatbot(style=selected_style)
    st.session_state.messages = []  # Clear chat history when style changes
    st.rerun()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What's on your mind?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get chatbot response
    with st.chat_message("assistant"):
        try:
            response = st.session_state.chatbot.invoke({"user_input": prompt})
            st.markdown(response.content)
            st.session_state.messages.append({"role": "assistant", "content": response.content})
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("Please make sure your OpenAI API key is set correctly in the .env file.")

# Add a clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()

# Add some helpful information in the sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
    This chatbot demonstrates different conversation styles:
    
    - **Basic**: Simple and straightforward responses
    - **Detailed**: Comprehensive answers with structure
    - **Friendly**: Conversational and engaging tone
    - **Professional**: Formal and business-like responses
    """)
    
    st.header("Technical Details")
    st.markdown("""
    Built with:
    - LangChain
    - OpenAI GPT-4o
    - Streamlit
    """) 