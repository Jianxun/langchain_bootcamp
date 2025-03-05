from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def pipe_operator_example():
    """Demonstrate chain composition using the pipe operator."""
    print("\n=== Pipe Operator Example ===")
    
    # Create LLM and prompt
    llm = ChatOpenAI(temperature=0.7)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that provides concise responses."),
        ("human", "What are three interesting facts about {topic}?")
    ])
    
    # Create chain using pipe operator
    chain = prompt | llm
    
    # Run the chain
    response = chain.invoke({"topic": "quantum computing"})
    print("Response:", response.content)

def traditional_chain_example():
    """Demonstrate chain composition using LLMChain."""
    print("\n=== Traditional Chain Example ===")
    
    # Create LLM and prompt
    llm = ChatOpenAI(temperature=0.7)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that provides concise responses."),
        ("human", "What are three interesting facts about {topic}?")
    ])
    
    # Create chain using LLMChain
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Run the chain
    response = chain.invoke({"topic": "quantum computing"})
    print("Response:", response["text"])

def explicit_steps_example():
    """Demonstrate chain composition using explicit steps."""
    print("\n=== Explicit Steps Example ===")
    
    # Create LLM and prompt
    llm = ChatOpenAI(temperature=0.7)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that provides concise responses."),
        ("human", "What are three interesting facts about {topic}?")
    ])
    
    # Step 1: Format the prompt
    formatted_prompt = prompt.format_messages(topic="quantum computing")
    print("Formatted Prompt:", formatted_prompt)
    
    # Step 2: Get response from LLM
    response = llm.invoke(formatted_prompt)
    print("Response:", response.content)

def complex_chain_example():
    """Demonstrate a more complex chain composition."""
    print("\n=== Complex Chain Example ===")
    
    # Create LLM
    llm = ChatOpenAI(temperature=0.7)
    
    # Create multiple prompts
    fact_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that provides concise responses."),
        ("human", "What are three interesting facts about {topic}?")
    ])
    
    analysis_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert analyst."),
        ("human", "Analyze these facts and identify the most significant one: {facts}")
    ])
    
    # Create chain using pipe operator
    chain = fact_prompt | llm | analysis_prompt | llm
    
    # Run the chain
    response = chain.invoke({"topic": "quantum computing"})
    print("Final Analysis:", response.content)

def main():
    print("Chain Composition Examples\n")
    
    # Run all examples
    pipe_operator_example()
    traditional_chain_example()
    explicit_steps_example()
    complex_chain_example()

if __name__ == "__main__":
    main() 