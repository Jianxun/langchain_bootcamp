from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_response(temperature: float) -> str:
    """Get a response from the model with specified temperature."""
    # Create a chat model with specified temperature
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=temperature
    )
    
    # Create a prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that provides concise responses."),
        ("human", "What are three interesting facts about Mars?")
    ])
    
    # Create and run the chain
    chain = prompt | llm
    response = chain.invoke({})
    
    return response.content

def main():
    print("Temperature Demo: How temperature affects model responses\n")
    
    # Test with different temperatures
    temperatures = [0.0, 0.5, 1.0, 1.5, 2.0]
    
    for temp in temperatures:
        print(f"\nTemperature: {temp}")
        print("-" * 50)
        print(get_response(temp))
        print("-" * 50)

if __name__ == "__main__":
    main() 