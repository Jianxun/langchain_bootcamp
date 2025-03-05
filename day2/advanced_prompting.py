from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, FewShotPromptTemplate
from langchain.prompts.example_selector import LengthBasedExampleSelector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def basic_prompt_example():
    """Demonstrate basic prompt template usage."""
    llm = ChatOpenAI(temperature=0.7)
    
    # Basic prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that provides concise responses."),
        ("human", "What are three interesting facts about {topic}?")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"topic": "quantum computing"})
    print("\nBasic Prompt Example:")
    print(response.content)

def few_shot_example():
    """Demonstrate few-shot learning with example selector."""
    # Example data
    examples = [
        {"input": "The cat sat on the mat", "output": "A cat is resting on a mat"},
        {"input": "The dog ran in the park", "output": "A dog is running in a park"},
        {"input": "The bird flew in the sky", "output": "A bird is flying in the sky"}
    ]
    
    # Create example selector
    example_selector = LengthBasedExampleSelector(
        examples=examples,
        max_length=50
    )
    
    # Create prompt template
    example_prompt = ChatPromptTemplate.from_messages([
        ("human", "{input}"),
        ("assistant", "{output}")
    ])
    
    # Create few-shot prompt
    prompt = FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=example_prompt,
        prefix="Translate the following sentences to a more descriptive form:",
        suffix="Human: {input}\nAssistant:",
        input_variables=["input"]
    )
    
    # Create chain
    llm = ChatOpenAI(temperature=0.7)
    chain = prompt | llm
    
    # Test the chain
    response = chain.invoke({"input": "The fish swam in the ocean"})
    print("\nFew-Shot Learning Example:")
    print(response.content)

def chain_of_thought_example():
    """Demonstrate chain of thought prompting."""
    llm = ChatOpenAI(temperature=0.7)
    
    # Chain of thought prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant that solves problems step by step.
        First, think about the problem carefully.
        Then, explain your reasoning.
        Finally, provide the answer."""),
        ("human", "If a clock shows 3:45, what is the angle between the hour and minute hands?")
    ])
    
    chain = prompt | llm
    response = chain.invoke({})
    print("\nChain of Thought Example:")
    print(response.content)

def main():
    print("Advanced Prompting Techniques Demo\n")
    
    # Run examples
    basic_prompt_example()
    few_shot_example()
    chain_of_thought_example()

if __name__ == "__main__":
    main() 