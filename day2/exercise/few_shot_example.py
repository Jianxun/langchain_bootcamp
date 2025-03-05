from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, FewShotPromptTemplate, PromptTemplate
from langchain.prompts.example_selector import LengthBasedExampleSelector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def demonstrate_few_shot_learning():
    """Demonstrate few-shot learning with detailed explanations."""
    print("Few-Shot Learning Demonstration\n")
    
    # Step 1: Define examples
    # These are the "few shots" that will guide the model
    examples = [
        {
            "input": "The cat sat on the mat",
            "output": "A cat is resting on a mat"
        },
        {
            "input": "The dog ran in the park",
            "output": "A dog is running in a park"
        },
        {
            "input": "The bird flew in the sky",
            "output": "A bird is flying in the sky"
        }
    ]
    
    print("=== Training Examples ===")
    for example in examples:
        print(f"Input:  {example['input']}")
        print(f"Output: {example['output']}\n")
    
    # Step 2: Create the example prompt template
    # This template defines how each example should be formatted
    example_prompt = PromptTemplate(
        input_variables=["input", "output"],
        template="Input: {input}\nOutput: {output}"
    )
    
    print("=== Example Format ===")
    print("Template:", example_prompt.template)
    print("Variables:", example_prompt.input_variables)
    
    # Step 3: Create the example selector
    # This helps manage the context window by selecting appropriate examples
    example_selector = LengthBasedExampleSelector(
        examples=examples,
        max_length=50,  # Maximum length of all examples combined
        example_prompt=example_prompt
    )
    
    # Step 4: Create the few-shot prompt template
    # This combines the examples with instructions for the model
    prompt = FewShotPromptTemplate(
        example_selector=example_selector,  # How to select examples
        example_prompt=example_prompt,      # How to format each example
        prefix="Translate the following sentences to a more descriptive form:",  # Instructions
        suffix="Input: {input}\nOutput:",   # How to format the actual input
        input_variables=["input"]           # Variables in the suffix
    )
    
    print("\n=== Prompt Structure ===")
    print("Prefix:", prompt.prefix)
    print("Suffix:", prompt.suffix)
    
    # Step 5: Create and run the chain
    llm = ChatOpenAI(temperature=0.7)
    chain = prompt | llm
    
    # Test with new inputs
    test_inputs = [
        "The fish swam in the ocean",
        "The butterfly landed on the flower",
        "The children played in the garden"
    ]
    
    print("\n=== Testing with New Inputs ===")
    for test_input in test_inputs:
        print(f"\nInput: {test_input}")
        response = chain.invoke({"input": test_input})
        print(f"Output: {response.content}")

def demonstrate_few_shot_with_different_task():
    """Demonstrate few-shot learning with a different task."""
    print("\n=== Few-Shot Learning with Different Task ===\n")
    
    # Define examples for sentiment analysis
    examples = [
        {
            "input": "I love this product, it's amazing!",
            "output": "Positive sentiment"
        },
        {
            "input": "This is terrible, I want my money back.",
            "output": "Negative sentiment"
        },
        {
            "input": "It's okay, nothing special.",
            "output": "Neutral sentiment"
        }
    ]
    
    # Create example prompt template
    example_prompt = PromptTemplate(
        input_variables=["input", "output"],
        template="Text: {input}\nSentiment: {output}"
    )
    
    # Create example selector
    example_selector = LengthBasedExampleSelector(
        examples=examples,
        max_length=100,
        example_prompt=example_prompt
    )
    
    # Create few-shot prompt template
    prompt = FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=example_prompt,
        prefix="Analyze the sentiment of the following texts:",
        suffix="Text: {input}\nSentiment:",
        input_variables=["input"]
    )
    
    # Create and run the chain
    llm = ChatOpenAI(temperature=0.7)
    chain = prompt | llm
    
    # Test with new inputs
    test_inputs = [
        "This is the best day ever!",
        "I'm not sure how I feel about this.",
        "This is absolutely horrible."
    ]
    
    print("Testing Sentiment Analysis:")
    for test_input in test_inputs:
        print(f"\nText: {test_input}")
        response = chain.invoke({"input": test_input})
        print(f"Sentiment: {response.content}")

def main():
    demonstrate_few_shot_learning()
    demonstrate_few_shot_with_different_task()

if __name__ == "__main__":
    main() 