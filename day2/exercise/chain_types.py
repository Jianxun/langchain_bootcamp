from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import SequentialChain, LLMChain
from typing import Dict, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def sequential_chain_example():
    """Demonstrate sequential chain usage."""
    llm = ChatOpenAI(temperature=0.7)
    
    # First chain: Generate a story
    story_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a creative writer."),
        ("human", "Write a short story about {topic} in {style} style.")
    ])
    story_chain = story_prompt | llm
    
    # Second chain: Analyze the story
    analysis_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a literary critic."),
        ("human", "Analyze this story and identify its main themes: {story}")
    ])
    analysis_chain = analysis_prompt | llm
    
    # Create sequential chain
    chain = SequentialChain(
        chains=[story_chain, analysis_chain],
        input_variables=["topic", "style"],
        output_variables=["story", "analysis"]
    )
    
    # Run the chain
    result = chain.invoke({
        "topic": "a robot learning to paint",
        "style": "science fiction"
    })
    
    print("\nSequential Chain Example:")
    print("Story:", result["story"])
    print("\nAnalysis:", result["analysis"])

def parallel_chain_example():
    """Demonstrate parallel chain usage."""
    llm = ChatOpenAI(temperature=0.7)
    
    # Create multiple chains for different aspects
    chains = {}
    
    # Technical analysis chain
    technical_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a technical analyst."),
        ("human", "Analyze the technical aspects of {topic}")
    ])
    chains["technical"] = technical_prompt | llm
    
    # Market analysis chain
    market_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a market analyst."),
        ("human", "Analyze the market potential of {topic}")
    ])
    chains["market"] = market_prompt | llm
    
    # Run chains in parallel
    topic = "artificial intelligence in healthcare"
    results = {}
    
    for name, chain in chains.items():
        results[name] = chain.invoke({"topic": topic})
    
    print("\nParallel Chain Example:")
    for name, result in results.items():
        print(f"\n{name.title()} Analysis:")
        print(result.content)

def custom_chain_example():
    """Demonstrate custom chain usage."""
    class CustomChain:
        def __init__(self, llm):
            self.llm = llm
            self.prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant."),
                ("human", "{input}")
            ])
        
        def __call__(self, inputs: Dict) -> Dict:
            # Pre-process input
            processed_input = inputs["input"].upper()
            
            # Run LLM
            chain = self.prompt | self.llm
            response = chain.invoke({"input": processed_input})
            
            # Post-process output
            return {
                "original_input": inputs["input"],
                "processed_input": processed_input,
                "response": response.content
            }
    
    # Create and use custom chain
    llm = ChatOpenAI(temperature=0.7)
    custom_chain = CustomChain(llm)
    
    result = custom_chain({"input": "Hello, how are you?"})
    
    print("\nCustom Chain Example:")
    print("Original Input:", result["original_input"])
    print("Processed Input:", result["processed_input"])
    print("Response:", result["response"])

def main():
    print("Chain Types Demo\n")
    
    # Run examples
    sequential_chain_example()
    parallel_chain_example()
    custom_chain_example()

if __name__ == "__main__":
    main() 