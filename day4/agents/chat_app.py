import streamlit as st
from vector_store import query_product_vector_store
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.schema import SystemMessage, HumanMessage, AIMessage
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Set page config
st.set_page_config(
    page_title="ADI Product Expert",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS for better chat display
st.markdown("""
<style>
.stTextInput>div>div>input {
    background-color: #f0f2f6;
}
.chat-message {
    padding: 1.5rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
}
.chat-message.user {
    background-color: #e6f3ff;
}
.chat-message.assistant {
    background-color: #f0f2f6;
}
.chat-message .message-content {
    margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🔍 ADI Product Expert")
st.markdown("""
Chat with an AI expert to find the right ADI products for your needs.
""")

# Initialize LLM and agent
if "llm" not in st.session_state:
    st.session_state.llm = ChatOpenAI(
        temperature=0.7,
        model="gpt-4"
    )

# Create tools for the agent
tools = [
    Tool(
        name="query_product_vector_store",
        func=query_product_vector_store,
        description="""Use this tool to search for ADI products. 
        Input should be a natural language query about the product you're looking for.
        Returns product information in markdown format."""
    )
]

# Create the agent
if "agent" not in st.session_state:
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an ADI Product Expert assistant. Your role is to help users find the right ADI products for their needs.
        You have access to a product search tool that can find ADI products based on user queries.
        
        When a user asks about products:
        1. Use the query_product_vector_store tool to search for relevant products
        2. Analyze the results and provide a helpful response
        3. If needed, ask follow-up questions to better understand the user's requirements
        
        Always be professional and technical in your responses."""),
        ("human", "{input}"),
        ("ai", "{agent_scratchpad}")
    ])
    
    st.session_state.agent = create_openai_functions_agent(
        llm=st.session_state.llm,
        tools=tools,
        prompt=prompt
    )
    st.session_state.agent_executor = AgentExecutor(
        agent=st.session_state.agent,
        tools=tools,
        verbose=True
    )

# Display chat messages
for message in st.session_state.messages:
    with st.container():
        st.markdown(f"""
        <div class="chat-message {message['role']}">
            <div class="message-content">
                {message['content']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("What kind of ADI product are you looking for?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.container():
        st.markdown(f"""
        <div class="chat-message user">
            <div class="message-content">
                {prompt}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Process the query
    with st.spinner("Thinking..."):
        try:
            # Get response from the agent
            response = st.session_state.agent_executor.invoke({"input": prompt})
            
            # Add assistant message to chat history
            st.session_state.messages.append({"role": "assistant", "content": response["output"]})
            
            # Display assistant message
            with st.container():
                st.markdown(f"""
                <div class="chat-message assistant">
                    <div class="message-content">
                        {response["output"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
        except Exception as e:
            error_message = f"Error processing your request: {str(e)}"
            st.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})

# Add a sidebar with information
with st.sidebar:
    st.header("About")
    st.markdown("""
    This is an AI-powered assistant that helps you find the right ADI products for your needs.
    You can ask questions about:
    - Product specifications
    - Application requirements
    - Technical features
    - Integration details
    """)
    
    st.header("Example Queries")
    st.markdown("""
    Try asking:
    - "I need an instrumentation amplifier for a sensor interface"
    - "What's the best ADC for a low power application?"
    - "Can you recommend a temperature sensor with I2C interface?"
    - "What are the key features of the AD8422?"
    """)
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun() 