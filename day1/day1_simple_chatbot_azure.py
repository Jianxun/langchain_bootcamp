from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_chatbot(style="basic"):
    """
    Create a chatbot with different prompt styles using Azure OpenAI.
    
    Args:
        style (str): The prompt style to use ("basic", "detailed", "friendly", "professional")
    """
    # Initialize the Azure OpenAI LLM with required parameters
    llm = AzureChatOpenAI(
        temperature=0.7,  # Controls randomness (0.0 = deterministic, 1.0 = very random)
        max_tokens=150,   # Maximum length of the response
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),  # Your Azure OpenAI deployment name
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),  # Azure OpenAI API version
        openai_api_base=os.getenv("AZURE_OPENAI_API_BASE"),       # Azure OpenAI API base URL
        openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),         # Azure OpenAI API key
        openai_api_type="azure"                                   # Must be set to "azure"
    )
    
    # Different prompt templates for different styles
    if style == "basic":
        # Basic template - simple and straightforward
        prompt = PromptTemplate(
            input_variables=["user_input"],
            template="""You are a helpful AI assistant. Please respond to the following question or statement:
            
            {user_input}
            
            Response:"""
        )
    elif style == "detailed":
        # Detailed template - with context and format instructions
        prompt = PromptTemplate(
            input_variables=["user_input"],
            template="""You are a helpful AI assistant with expertise in various subjects. 
            Please provide a detailed and well-structured response to the following question or statement.
            Include relevant examples or explanations where appropriate.
            
            Question/Statement: {user_input}
            
            Please provide your response in the following format:
            1. Main Answer
            2. Supporting Details
            3. Examples (if applicable)
            
            Response:"""
        )
    elif style == "friendly":
        # Friendly template - conversational and engaging
        prompt = PromptTemplate(
            input_variables=["user_input"],
            template="""Hey there! I'm your friendly AI assistant. I'm here to help you with any questions or topics you have.
            Let's make this conversation fun and engaging!
            
            What's on your mind? {user_input}
            
            Let me help you with that!"""
        )
    else:  # professional
        # Professional template - formal and business-like
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are a professional AI consultant with expertise in business and technology. "
                "Provide clear, concise, and actionable responses."
            ),
            HumanMessagePromptTemplate.from_template("{user_input}")
        ])
    
    # Create a chain using the new pipe operator pattern
    chain = prompt | llm
    
    return chain

def main():
    print("Welcome to the Azure OpenAI LangChain Chatbot!")
    print("Type 'quit' to exit.")
    print("Type 'style' to switch between different prompt styles:")
    print("  - basic: Simple and straightforward")
    print("  - detailed: Comprehensive with structure")
    print("  - friendly: Conversational and engaging")
    print("  - professional: Formal and business-like")
    print("-" * 50)
    
    # Create the chatbot with default style
    current_style = "basic"
    chatbot = create_chatbot(style=current_style)
    
    while True:
        # Get user input
        user_input = input("\nYou: ").strip()
        
        # Check if user wants to quit
        if user_input.lower() == 'quit':
            print("\nGoodbye!")
            break
            
        # Check if user wants to switch styles
        if user_input.lower() == 'style':
            styles = ["basic", "detailed", "friendly", "professional"]
            current_index = styles.index(current_style)
            current_style = styles[(current_index + 1) % len(styles)]
            print(f"\nSwitching to style: {current_style}")
            chatbot = create_chatbot(style=current_style)
            continue
        
        # Generate response
        try:
            # Use invoke with the new chain pattern
            response = chatbot.invoke({"user_input": user_input})
            print("\nAssistant:", response.content)
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please make sure your Azure OpenAI API credentials are set correctly in the .env file.")
            print("Required environment variables:")
            print("  - AZURE_OPENAI_API_KEY")
            print("  - AZURE_OPENAI_API_BASE")
            print("  - AZURE_OPENAI_API_VERSION")
            print("  - AZURE_OPENAI_DEPLOYMENT_NAME")

if __name__ == "__main__":
    main() 