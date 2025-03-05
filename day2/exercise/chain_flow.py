from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def demonstrate_chain_flow():
    """Demonstrate how data flows through a chain."""
    print("Chain Flow Demonstration\n")
    
    # Create LLM
    llm = ChatOpenAI(temperature=0.7)
    
    # Step 1: Create a prompt that asks for facts
    fact_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that provides concise responses."),
        ("human", "What are three interesting facts about {topic}?")
    ])
    
    # Step 2: Create a prompt that asks for analysis
    analysis_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert analyst."),
        ("human", "Analyze these facts and identify the most significant one: {facts}")
    ])
    
    # Step 3: Create a prompt that asks for implications
    implications_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a strategic thinker."),
        ("human", "Based on this analysis: {analysis}, what are the key implications for the future?")
    ])
    
    # Create the chain
    chain = fact_prompt | llm | analysis_prompt | llm | implications_prompt | llm
    
    # Run the chain and capture intermediate results
    print("=== Chain Execution Steps ===\n")
    
    # Step 1: Format the initial prompt
    initial_input = {"topic": "quantum computing"}
    print("1. Initial Input:", initial_input)
    
    # Step 2: Get facts
    facts = fact_prompt.invoke(initial_input)
    print("\n2. After fact_prompt:", facts)
    
    facts_response = llm.invoke(facts)
    print("\n3. After first llm:", facts_response.content)
    
    # Step 3: Analyze facts
    analysis_input = {"facts": facts_response.content}
    analysis = analysis_prompt.invoke(analysis_input)
    print("\n4. After analysis_prompt:", analysis)
    
    analysis_response = llm.invoke(analysis)
    print("\n5. After second llm:", analysis_response.content)
    
    # Step 4: Get implications
    implications_input = {"analysis": analysis_response.content}
    implications = implications_prompt.invoke(implications_input)
    print("\n6. After implications_prompt:", implications)
    
    final_response = llm.invoke(implications)
    print("\n7. Final Response:", final_response.content)
    
    print("\n=== Chain Summary ===")
    print("The chain follows this pattern:")
    print("prompt -> llm -> prompt -> llm -> prompt -> llm")
    print("\nEach prompt formats the input for the next llm,")
    print("and each llm generates output that becomes input for the next prompt.")

def main():
    demonstrate_chain_flow()

if __name__ == "__main__":
    main() 