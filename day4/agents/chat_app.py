import streamlit as st
import asyncio
from demo import ADIEngineerAgent
import json

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = ADIEngineerAgent()

# Set page config
st.set_page_config(
    page_title="ADI Engineer Agent",
    page_icon="🔧",
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
.json-viewer {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
    font-family: monospace;
    white-space: pre-wrap;
}
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🔧 ADI Engineer Agent")
st.markdown("""
This agent helps you explore ADI solutions and recommend products based on your technical requirements.
Ask questions about products, solutions, or technical specifications.
""")

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
if prompt := st.chat_input("What would you like to know about ADI products?"):
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
    with st.spinner("Processing your request..."):
        try:
            # Run the agent
            result = asyncio.run(st.session_state.agent.run(prompt))
            
            # Format the response
            response = "Here's what I found:\n\n"
            
            # Add requirements
            response += "**Requirements:**\n"
            response += f"- Application Area: {result['requirements']['application_area']}\n"
            for req in result['requirements']['requirements']:
                response += f"- {req['parameter']}: {req['min']} to {req['max']} {req['unit']}\n"
            
            # Add matching products
            if result['products']:
                response += "\n**Matching Products:**\n"
                for product in result['products']:
                    response += f"- {product['name']} ({product['id']})\n"
                    response += f"  Description: {product['description']}\n"
                    response += f"  Features: {', '.join(product['features'])}\n"
                    response += f"  Applications: {', '.join(product['applications'])}\n"
                    response += f"  Datasheet: [{product['datasheet_url']}]({product['datasheet_url']})\n"
            
            # Add matching solutions
            if result['solutions']:
                response += "\n**Matching Solutions:**\n"
                for solution in result['solutions']:
                    response += f"- {solution['name']} ({solution['id']})\n"
                    response += f"  Description: {solution['description']}\n"
                    response += "  Products:\n"
                    for product in solution['products']:
                        response += f"  - {product['name']} ({product['role']})\n"
                    response += "  Reference Designs:\n"
                    for design in solution['reference_designs']:
                        response += f"  - [{design['name']}]({design['url']})\n"
            
            # Add parameter analysis
            if result['analysis']['validation']:
                response += "\n**Parameter Analysis:**\n"
                for product_id, validation in result['analysis']['validation'].items():
                    response += f"- {product_id}:\n"
                    for param, details in validation.items():
                        response += f"  - {param}: {details['message']}\n"
            
            # Add compatibility status
            if result['analysis']['compatibility']:
                response += "\n**Compatibility Status:**\n"
                for product_id, status in result['analysis']['compatibility'].items():
                    response += f"- {product_id}: {status['message']}\n"
            
            # Add assistant message to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Display assistant message
            with st.container():
                st.markdown(f"""
                <div class="chat-message assistant">
                    <div class="message-content">
                        {response}
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
    The ADI Engineer Agent helps you:
    - Find products based on technical requirements
    - Explore complete solutions
    - Access reference designs
    - Analyze parameter compatibility
    """)
    
    st.header("Example Queries")
    st.markdown("""
    Try asking about:
    - "I need an instrumentation amplifier for a sensor interface with 3.3V supply"
    - "Looking for a solution for a precision measurement system with 5V supply"
    - "Find an amplifier with temperature range -40°C to 85°C"
    """)
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun() 