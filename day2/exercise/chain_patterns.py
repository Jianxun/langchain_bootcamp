from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import SequentialChain
import os
from dotenv import load_dotenv
from typing import Dict, List

# Load environment variables
load_dotenv()

def parallel_chains_example():
    """Demonstrate parallel chain execution."""
    print("\n=== Parallel Chains Example ===")
    
    # Create LLM
    llm = ChatOpenAI(temperature=0.7)
    
    # Create different prompts for parallel analysis
    technical_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a technical expert."),
        ("human", "Analyze the technical aspects of {topic}")
    ])
    
    market_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a market analyst."),
        ("human", "Analyze the market potential of {topic}")
    ])
    
    social_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a social impact analyst."),
        ("human", "Analyze the social implications of {topic}")
    ])
    
    # Create parallel chains
    technical_chain = technical_prompt | llm
    market_chain = market_prompt | llm
    social_chain = social_prompt | llm
    
    # Run chains in parallel
    topic = "artificial intelligence in healthcare"
    results = {
        "technical": technical_chain.invoke({"topic": topic}),
        "market": market_chain.invoke({"topic": topic}),
        "social": social_chain.invoke({"topic": topic})
    }
    
    # Print results
    for name, result in results.items():
        print(f"\n{name.title()} Analysis:")
        print(result.content)

def branching_chains_example():
    """Demonstrate branching chain execution."""
    print("\n=== Branching Chains Example ===")
    
    # Create LLM
    llm = ChatOpenAI(temperature=0.7)
    
    # Initial prompt to determine the type of analysis needed
    initial_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a decision maker."),
        ("human", "Based on this topic: {topic}, what type of analysis would be most valuable? Choose one: technical, market, or social.")
    ])
    
    # Create specialized prompts
    technical_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a technical expert."),
        ("human", "Provide a detailed technical analysis of {topic}")
    ])
    
    market_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a market analyst."),
        ("human", "Provide a detailed market analysis of {topic}")
    ])
    
    social_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a social impact analyst."),
        ("human", "Provide a detailed social impact analysis of {topic}")
    ])
    
    # Create the chains
    initial_chain = initial_prompt | llm
    technical_chain = technical_prompt | llm
    market_chain = market_prompt | llm
    social_chain = social_prompt | llm
    
    # Run the branching chain
    topic = "artificial intelligence in healthcare"
    
    # First, determine which type of analysis to perform
    analysis_type = initial_chain.invoke({"topic": topic}).content.lower()
    print(f"Selected analysis type: {analysis_type}")
    
    # Then, run the appropriate chain
    if "technical" in analysis_type:
        result = technical_chain.invoke({"topic": topic})
    elif "market" in analysis_type:
        result = market_chain.invoke({"topic": topic})
    else:
        result = social_chain.invoke({"topic": topic})
    
    print("\nAnalysis Result:")
    print(result.content)

def sequential_with_branching_example():
    """Demonstrate sequential chain with branching."""
    print("\n=== Sequential with Branching Example ===")
    
    # Create LLM
    llm = ChatOpenAI(temperature=0.7)
    
    # Create prompts for different stages
    overview_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a general analyst."),
        ("human", "Provide a brief overview of {topic}")
    ])
    
    # Create specialized analysis prompts
    technical_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a technical expert."),
        ("human", "Based on this overview: {overview}, provide technical details about {topic}")
    ])
    
    market_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a market analyst."),
        ("human", "Based on this overview: {overview}, provide market analysis of {topic}")
    ])
    
    # Create synthesis prompt
    synthesis_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a strategic advisor."),
        ("human", """Based on:
        Overview: {overview}
        Technical Analysis: {technical}
        Market Analysis: {market}
        
        Provide strategic recommendations for {topic}""")
    ])
    
    # Create the chains
    overview_chain = overview_prompt | llm
    technical_chain = technical_prompt | llm
    market_chain = market_prompt | llm
    synthesis_chain = synthesis_prompt | llm
    
    # Run the sequential chain with parallel branches
    topic = "artificial intelligence in healthcare"
    
    # Step 1: Get overview
    overview = overview_chain.invoke({"topic": topic})
    print("\nOverview:", overview.content)
    
    # Step 2: Run parallel analyses
    technical = technical_chain.invoke({
        "topic": topic,
        "overview": overview.content
    })
    market = market_chain.invoke({
        "topic": topic,
        "overview": overview.content
    })
    
    print("\nTechnical Analysis:", technical.content)
    print("\nMarket Analysis:", market.content)
    
    # Step 3: Synthesize results
    synthesis = synthesis_chain.invoke({
        "topic": topic,
        "overview": overview.content,
        "technical": technical.content,
        "market": market.content
    })
    
    print("\nSynthesis:", synthesis.content)

def main():
    print("Chain Pattern Examples\n")
    
    # Run all examples
    parallel_chains_example()
    branching_chains_example()
    sequential_with_branching_example()

if __name__ == "__main__":
    main() 