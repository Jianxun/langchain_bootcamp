import streamlit as st
from day2_document_summarizer import summarize_document
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Document Summarizer",
    page_icon="📝",
    layout="wide"
)

# Initialize session state for input text
if "input_text" not in st.session_state:
    # Load the default text from file
    try:
        with open("day2/finite_state_machine.txt", "r") as file:
            st.session_state.input_text = file.read()
    except Exception as e:
        st.session_state.input_text = "Error loading default text. Please paste your text here."

# Title and description
st.title("📝 Document Summarizer")
st.markdown("""
This app uses LangChain and GPT-4o to generate summaries of text documents in different styles.
""")

# Style selector
styles = ["narrative", "bullet_points", "structured_data"]
selected_style = st.selectbox(
    "Select Summary Style",
    styles,
    help="Choose how you want the summary to be formatted"
)

# Main content area
st.subheader("Input Text")
input_text = st.text_area(
    "Paste your text here",
    value=st.session_state.input_text,
    height=400,
    help="Enter the text you want to summarize"
)

st.subheader("Summary")
if st.button("Summarize", type="primary"):
    if input_text.strip():
        with st.spinner("Generating summary..."):
            try:
                # Create a placeholder for the summary
                summary_placeholder = st.empty()
                
                # Get the summary
                summary = summarize_document(input_text, selected_style)
                
                # Display the summary
                summary_placeholder.markdown(summary.content)
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Please make sure your OpenAI API key is set correctly in the .env file.")
    else:
        st.warning("Please enter some text to summarize.")

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
    This document summarizer supports three different styles:
    
    - **Narrative**: A flowing, paragraph-style summary
    - **Bullet Points**: Key points organized in a list
    - **Structured Data**: Information organized in JSON format
    """)
    
    st.header("Technical Details")
    st.markdown("""
    Built with:
    - LangChain
    - OpenAI GPT-4o
    - Streamlit
    """)
    
    st.header("Usage Tips")
    st.markdown("""
    1. Paste your text in the input box
    2. Select your preferred summary style
    3. Click "Summarize"
    4. View the generated summary
    """)
    
    # Add a sample text button
    if st.button("Load Sample Text"):
        sample_text = """A finite state machine (FSM) is a mathematical model of computation that describes a system that can be in one state at a time out of a finite number of states. The system can change from one state to another when triggered by an event or condition. FSMs are used in various applications including:
        
        1. Vending machines
        2. Traffic lights
        3. Game state management
        4. Network protocols
        
        FSMs can be either deterministic or non-deterministic, depending on whether the next state is uniquely determined by the current state and input."""
        st.session_state.input_text = sample_text
        st.rerun() 