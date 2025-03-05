from langchain_openai import ChatOpenAI
from langchain.prompts import FewShotPromptTemplate, PromptTemplate
from langchain.prompts.example_selector import LengthBasedExampleSelector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_with_different_example_sizes():
    """Test few-shot learning with different numbers of examples."""
    print("Testing Different Example Sizes\n")
    
    # Define a larger set of examples
    all_examples = [
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
        },
        {
            "input": "The rabbit hopped in the garden",
            "output": "A rabbit is hopping in the garden"
        },
        {
            "input": "The squirrel climbed the tree",
            "output": "A squirrel is climbing the tree"
        },
        {
            "input": "The turtle walked on the beach",
            "output": "A turtle is walking on the beach"
        }
    ]
    
    # Create example prompt template
    example_prompt = PromptTemplate(
        input_variables=["input", "output"],
        template="Input: {input}\nOutput: {output}"
    )
    
    # Test inputs
    test_inputs = [
        "The fish swam in the ocean",
        "The butterfly landed on the flower",
        "The children played in the garden"
    ]
    
    # Test with different numbers of examples
    example_sizes = [1, 2, 3, 4, 5, 6]
    
    for size in example_sizes:
        print(f"\n=== Testing with {size} example{'s' if size > 1 else ''} ===")
        
        # Select examples
        examples = all_examples[:size]
        
        # Create example selector
        example_selector = LengthBasedExampleSelector(
            examples=examples,
            max_length=50,
            example_prompt=example_prompt
        )
        
        # Create few-shot prompt template
        prompt = FewShotPromptTemplate(
            example_selector=example_selector,
            example_prompt=example_prompt,
            prefix="Translate the following sentences to a more descriptive form:",
            suffix="Input: {input}\nOutput:",
            input_variables=["input"]
        )
        
        # Create and run the chain
        llm = ChatOpenAI(temperature=0.7)
        chain = prompt | llm
        
        # Test with each input
        for test_input in test_inputs:
            print(f"\nInput: {test_input}")
            response = chain.invoke({"input": test_input})
            print(f"Output: {response.content}")

def demonstrate_example_selection_strategies():
    """Demonstrate different strategies for selecting examples."""
    print("\n=== Example Selection Strategies ===\n")
    
    # Define a larger set of diverse examples
    all_examples = [
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
        },
        {
            "input": "The elephant walked through the jungle",
            "output": "An elephant is walking through the jungle"
        },
        {
            "input": "The mouse scurried under the table",
            "output": "A mouse is scurrying under the table"
        },
        {
            "input": "The lion roared in the savanna",
            "output": "A lion is roaring in the savanna"
        }
    ]
    
    # Create example prompt template
    example_prompt = PromptTemplate(
        input_variables=["input", "output"],
        template="Input: {input}\nOutput: {output}"
    )
    
    # Test input
    test_input = "The penguin waddled on the ice"
    
    # Strategy 1: First N examples
    print("Strategy 1: First 3 examples")
    examples = all_examples[:3]
    example_selector = LengthBasedExampleSelector(
        examples=examples,
        max_length=50,
        example_prompt=example_prompt
    )
    prompt = FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=example_prompt,
        prefix="Translate the following sentences to a more descriptive form:",
        suffix="Input: {input}\nOutput:",
        input_variables=["input"]
    )
    chain = prompt | ChatOpenAI(temperature=0.7)
    response = chain.invoke({"input": test_input})
    print(f"Output: {response.content}")
    
    # Strategy 2: Diverse examples (first, middle, last)
    print("\nStrategy 2: Diverse examples (first, middle, last)")
    examples = [all_examples[0], all_examples[3], all_examples[-1]]
    example_selector = LengthBasedExampleSelector(
        examples=examples,
        max_length=50,
        example_prompt=example_prompt
    )
    prompt = FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=example_prompt,
        prefix="Translate the following sentences to a more descriptive form:",
        suffix="Input: {input}\nOutput:",
        input_variables=["input"]
    )
    chain = prompt | ChatOpenAI(temperature=0.7)
    response = chain.invoke({"input": test_input})
    print(f"Output: {response.content}")

def main():
    test_with_different_example_sizes()
    demonstrate_example_selection_strategies()

if __name__ == "__main__":
    main() 