import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.memory import BaseMemory
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Initialize Streamlit page configuration
st.set_page_config(
    page_title="LangChain Chat with Memory",
    page_icon="🧠",
    layout="wide"
)

# Initialize ChatOpenAI
llm = ChatOpenAI(
    temperature=0.7,
    model="gpt-4",
    streaming=True
)

# Initialize session state for memories and messages
if 'buffer_memory' not in st.session_state:
    st.session_state.buffer_memory = ConversationBufferMemory(
        return_messages=True,
        memory_key="chat_history",
        output_key="output"
    )
if 'summary_memory' not in st.session_state:
    st.session_state.summary_memory = ConversationSummaryMemory(
        llm=llm,
        return_messages=True,
        memory_key="chat_summary",
        output_key="output"
    )
if 'messages' not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="You are a helpful AI assistant. Be concise and clear in your responses.")
    ]

async def process_message_stream(user_input: str) -> str:
    """Process user input and return AI response with streaming."""
    try:
        # Get the current messages
        messages = st.session_state.messages
        
        # Initialize response container
        full_response = []
        response_container = st.empty()
        
        # Get streaming response from LLM
        async for chunk in llm.astream(messages):
            if chunk.content:
                full_response.append(chunk.content)
                # Update the response in place without newlines
                response_container.markdown("".join(full_response) + "▌")
        
        # Get the complete response
        complete_response = "".join(full_response)
        response_container.markdown(complete_response)
        
        # Update both memories
        st.session_state.buffer_memory.save_context(
            {"input": user_input},
            {"output": complete_response}
        )
        st.session_state.summary_memory.save_context(
            {"input": user_input},
            {"output": complete_response}
        )
        
        return complete_response
        
    except Exception as e:
        st.error(f"Error processing message: {str(e)}")
        return "I apologize, but I encountered an error processing your message."

# Main UI
st.title("🤖 LangChain Chat")
with st.container():
    col1, col2 = st.columns([1, 1])

    with col1:
        st.write("Hello")
    with col2:
        # Initialize chat history in session state if not exists
        if "messages" not in st.session_state:
            st.session_state.messages = [
                SystemMessage(content="You are a helpful AI assistant. Be concise and clear in your responses.")
            ]

        # Create a dedicated container for all messages
        with st.container():
            # Display chat messages
            for message in st.session_state.messages:
                if isinstance(message, SystemMessage):
                    continue  # Skip system messages in display
                with st.chat_message("user" if isinstance(message, HumanMessage) else "assistant"):
                    st.write(message.content)

            # Chat input
            if prompt := st.chat_input("What's on your mind?"):
                # Add user message to chat history
                user_message = HumanMessage(content=prompt)
                st.session_state.messages.append(user_message)
                with st.chat_message("user"):
                    st.write(prompt)
                
                # Get AI response with streaming
                with st.chat_message("assistant"):
                    response = asyncio.run(process_message_stream(prompt))
                    st.session_state.messages.append(AIMessage(content=response))
