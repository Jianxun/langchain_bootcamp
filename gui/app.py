import streamlit as st
import os
from datetime import datetime
from pathlib import Path
import asyncio
from utils.llm import AIAssistant

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "instruction_version" not in st.session_state:
    st.session_state.instruction_version = None

if "assistant" not in st.session_state:
    st.session_state.assistant = AIAssistant()

if "show_instructions_editor" not in st.session_state:
    st.session_state.show_instructions_editor = False

if "last_instruction_update" not in st.session_state:
    st.session_state.last_instruction_update = datetime.now()

def load_instructions():
    """Load and parse both system prompt and session context files"""
    base_path = Path(__file__).parent
    system_path = base_path / "system_prompt.md"
    session_path = base_path / "session_context.md"
    
    system_content = "System prompt file not found."
    session_content = "Session context file not found."
    
    if system_path.exists():
        with open(system_path, "r") as f:
            system_content = f.read()
    
    if session_path.exists():
        with open(session_path, "r") as f:
            session_content = f.read()
    
    # Update the version tracking (based on session context)
    current_version = session_content.split("Version: ")[-1].split("\n")[0] if "Version: " in session_content else "unknown"
    if st.session_state.instruction_version != current_version:
        st.session_state.instruction_version = current_version
        st.session_state.last_instruction_update = datetime.now()
    
    return system_content, session_content

def check_instruction_updates():
    """Check if session context has been updated"""
    session_path = Path(__file__).parent / "session_context.md"
    if not session_path.exists():
        return False
    
    last_modified = datetime.fromtimestamp(session_path.stat().st_mtime)
    if last_modified > st.session_state.last_instruction_update:
        st.session_state.last_instruction_update = last_modified
        return True
    return False

async def get_ai_response(messages):
    """Get AI response using the assistant with streaming"""
    response_placeholder = st.empty()
    full_response = []
    
    async for chunk in st.session_state.assistant.get_response(messages):
        full_response.append(chunk)
        response_placeholder.markdown("".join(full_response) + "▌")
    
    complete_response = "".join(full_response)
    response_placeholder.markdown(complete_response)
    
    # Check for updates after response is complete
    if check_instruction_updates():
        st.rerun()
    
    return complete_response

async def update_instructions(update_request):
    """Update instructions using the assistant with streaming"""
    response_placeholder = st.empty()
    full_response = []
    
    async for chunk in st.session_state.assistant.update_instructions(update_request):
        full_response.append(chunk)
        response_placeholder.markdown("".join(full_response) + "▌")
    
    complete_response = "".join(full_response)
    response_placeholder.markdown(complete_response)
    
    # Force sidebar refresh
    st.session_state.last_instruction_update = datetime.now()
    st.rerun()
    
    return complete_response

def main():
    st.title("AI Assistant")
    
    # Sidebar with instructions and editor
    with st.sidebar:
        st.markdown("## System Prompt")
        system_content, session_content = load_instructions()
        st.markdown(system_content)
        
        st.markdown("## Session Context")
        # Toggle for session context editor
        if st.button("✏️ Edit Session Context"):
            st.session_state.show_instructions_editor = not st.session_state.show_instructions_editor
        
        if st.session_state.show_instructions_editor:
            st.markdown("### Update Session Context")
            update_request = st.text_area(
                "Describe the changes you want to make to the session context:",
                height=100,
                placeholder="Example: Update user's current learning progress"
            )
            
            if st.button("Update"):
                with st.spinner("Updating session context..."):
                    asyncio.run(update_instructions(update_request))
                # Reset the editor state
                st.session_state.show_instructions_editor = False
        
        # Display current session context
        st.markdown(session_content)
    
    # Main chat interface
    st.markdown("## Chat")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("What would you like to discuss?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response with streaming
        with st.chat_message("assistant"):
            response = asyncio.run(get_ai_response(st.session_state.messages))
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main() 