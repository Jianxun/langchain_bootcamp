from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from pathlib import Path
import os
from dotenv import load_dotenv
from typing import AsyncIterator, Tuple
from datetime import datetime
import asyncio
import sys
import difflib
import streamlit as st

# Load environment variables
load_dotenv()

def generate_diff(old_content: str, new_content: str) -> str:
    """Generate a human-readable diff between old and new content"""
    diff = difflib.unified_diff(
        old_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile='Previous Instructions',
        tofile='New Instructions',
        lineterm=''
    )
    return ''.join(diff)

def debug_print(message: str, content: str = None):
    """Print debug information to stderr with optional content"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[DEBUG] {timestamp} - {message}", file=sys.stderr, flush=True)
    if content:
        print("\n--- Content Start ---", file=sys.stderr)
        print(content, file=sys.stderr)
        print("--- Content End ---\n", file=sys.stderr, flush=True)

def load_instructions():
    """Load both system prompt and session context files"""
    instruction_path = Path(__file__).parent.parent
    system_path = instruction_path / "system_prompt.md"
    session_path = instruction_path / "session_context.md"
    
    system_content = ""
    session_content = ""
    
    if system_path.exists():
        with open(system_path, "r") as f:
            system_content = f.read()
    
    if session_path.exists():
        with open(session_path, "r") as f:
            session_content = f.read()
    
    return system_content, session_content

def save_session_context(content: str) -> Tuple[bool, str]:
    """Save content to the session context file and return success status and diff"""
    try:
        session_path = Path(__file__).parent.parent / "session_context.md"
        old_content = ""
        if session_path.exists():
            with open(session_path, "r") as f:
                old_content = f.read()
            # Backup current file
            backup_path = session_path.parent / f"session_context.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
            session_path.rename(backup_path)
            debug_print(f"Created backup at {backup_path}")
        
        # Generate diff
        diff = generate_diff(old_content, content)
        debug_print("Generated diff between old and new session context", diff)
        
        # Write new content
        with open(session_path, "w") as f:
            f.write(content)
        debug_print(f"Successfully saved new session context to {session_path}", content)
        return True, diff
    except Exception as e:
        debug_print(f"Error saving session context: {str(e)}")
        return False, ""

class AIAssistant:
    def __init__(self):
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
        self.llm = ChatOpenAI(
            temperature=0.7,
            model="gpt-4",
            streaming=True
        )
        self.system_prompt, self.session_context = load_instructions()
        self._request_counter = 0
        
        # Create the system prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an AI assistant. Follow these instructions:\n\n{system_prompt}\n\nSession Context:\n{session_context}"),
            ("human", "{input}")
        ])
        
        # Create the session context update prompt
        self.update_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI assistant that helps maintain the session_context.md file.
            This file contains session-specific information like:
            - User information (name, occupation, preferences)
            - Current learning progress
            - Active tasks and their status
            - Recent discussions and decisions
            
            When updating the file:
            1. Keep the existing structure and sections
            2. Update only the session-specific information
            3. Add timestamps for changes
            4. Maintain a clean markdown format
            
            Current session context:
            {current_context}"""),
            ("human", "Update request: {update_request}")
        ])

        # Create the conversation summary prompt
        self.summary_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI assistant that summarizes conversations and suggests updates to the session_context.md file.
            This file contains session-specific information that can change frequently.
            
            Current session context:
            {current_context}
            
            When analyzing conversations and suggesting updates:
            1. Focus only on session-specific information
            2. Only suggest updates for new or changed information
            3. Keep existing structure and sections
            4. Format suggestions as specific edit instructions
            5. Include rationale for each suggested change
            
            IMPORTANT: You MUST use the exact format below for updates to be processed:
            ```
            UPDATE SUGGESTIONS:
            1. Section "User Information":
               - Update name to "Jack"
               - Add occupation: "Mechanical Engineer"
               Rationale: User provided these details in conversation
            
            2. Section "Active Tasks":
               - Add new task: "Discuss engineering requirements"
               Rationale: Based on user's profession, likely upcoming topic
            ```
            
            If no updates are needed, respond with "No updates needed." instead of empty or different format.
            
            Remember:
            - Start with "UPDATE SUGGESTIONS:" for any changes
            - Number each section change
            - Include specific edit instructions
            - Always provide rationale
            - Only suggest changes for new or modified information"""),
            ("human", """Here is the conversation history:
            {conversation_history}
            
            Analyze this conversation and provide update suggestions in the exact format specified above.
            If no updates are needed, respond with "No updates needed." """)
        ])
        
    def _create_messages(self, conversation_history):
        """Create a list of messages including system instructions and conversation history"""
        # Format the initial system prompt
        messages = self.prompt.format_messages(
            system_prompt=self.system_prompt,
            session_context=self.session_context,
            input="Initialize conversation."
        )
        
        # Add last 5 conversation rounds
        for msg in conversation_history[-10:]:  # -10 because each round has 2 messages (user + assistant)
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
                
        return messages
    
    async def get_response(self, conversation_history) -> AsyncIterator[str]:
        """Get AI response based on conversation history with streaming"""
        try:
            messages = self._create_messages(conversation_history)
            async for chunk in self.llm.astream(messages):
                yield chunk.content
            
            # After generating response, trigger background instruction update
            debug_print("Triggering background instruction update from conversation")
            # Create and await the background task instead of just creating it
            try:
                # Set a timeout for the background task
                await asyncio.wait_for(
                    self._update_instructions_from_conversation(conversation_history),
                    timeout=30.0  # 30 seconds timeout
                )
            except asyncio.TimeoutError:
                debug_print("Background instruction update timed out after 30 seconds")
            except Exception as e:
                debug_print(f"Background instruction update failed: {str(e)}")
                import traceback
                debug_print("Background task error traceback", traceback.format_exc())
        except Exception as e:
            debug_print(f"Error in get_response: {str(e)}")
            yield f"Error: {str(e)}"
            
    async def update_instructions(self, update_request: str) -> AsyncIterator[str]:
        """Update the session_context.md file based on the request"""
        try:
            debug_print("Processing session context update request", update_request)
            
            # If this is a formatted suggestion, extract the actual updates
            if "UPDATE SUGGESTIONS:" in update_request:
                debug_print("Processing formatted update suggestions")
                suggestions = update_request.split("UPDATE SUGGESTIONS:", 1)[1].strip()
                update_request = f"Apply the following updates to the session context:\n{suggestions}"
            
            # Create messages for updating session context
            messages = self.update_prompt.format_messages(
                current_context=self.session_context,
                update_request=update_request
            )
            
            # Generate the updated content
            full_response = []
            async for chunk in self.llm.astream(messages):
                full_response.append(chunk.content)
                yield chunk.content
            
            # Save the updated content
            updated_content = "".join(full_response)
            success, diff = save_session_context(updated_content)
            if success:
                # Reload session context
                self.system_prompt, self.session_context = load_instructions()
                debug_print("Session context updated and reloaded successfully", updated_content)
                yield f"\n\nSession context updated successfully!\n\nChanges made:\n```diff\n{diff}\n```"
            else:
                debug_print("Failed to save session context")
                yield "\n\nError: Failed to save session context."
                
        except Exception as e:
            debug_print(f"Error in update_instructions: {str(e)}")
            yield f"Error updating session context: {str(e)}"

    async def _update_instructions_from_conversation(self, conversation_history):
        """Background task to update instructions based on conversation context"""
        try:
            self._request_counter += 1
            request_id = self._request_counter
            debug_print(f"Processing background instruction update (Request #{request_id})")
            
            # Format messages for conversation analysis
            messages = self.summary_prompt.format_messages(
                current_context=self.session_context,
                conversation_history=str(conversation_history[-10:])  # Last 5 conversation rounds
            )
            
            # Get update suggestions
            response = await self.llm.ainvoke(messages)
            debug_print(f"Received update suggestions (Request #{request_id})", response.content)
            
            # Only proceed if there are actual updates
            if "No updates needed." not in response.content:
                # Use the explicit update mechanism for consistency
                async for chunk in self.update_instructions(response.content):
                    # We don't yield the chunks since this is a background task
                    continue
                
                # Update Streamlit session state if available
                if "last_instruction_update" in st.session_state:
                    st.session_state.last_instruction_update = datetime.now()
                    # Force a rerun to refresh the UI with new context
                    st.rerun()
            else:
                debug_print(f"No updates needed (Request #{request_id})")
                
        except Exception as e:
            debug_print(f"Error in _update_instructions_from_conversation (Request #{request_id}): {str(e)}")
            import traceback
            debug_print("Error traceback", traceback.format_exc()) 