from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def demonstrate_chain_of_thought():
    """Demonstrate chain of thought prompting with different types of problems."""
    print("Chain of Thought Examples\n")
    
    # Use GPT-4 for better reasoning
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    
    # Example 1: Mathematical Problem
    print("=== Example 1: Mathematical Problem ===\n")
    math_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant that solves problems step by step.
        First, think about the problem carefully.
        Then, explain your reasoning.
        Finally, provide the answer.
        
        Format your response as:
        Thought: [your step-by-step reasoning]
        Answer: [final answer]"""),
        ("human", "If a clock shows 3:45, what is the angle between the hour and minute hands?")
    ])
    
    chain = math_prompt | llm
    response = chain.invoke({})
    print(response.content)
    
    # Example 2: Logical Problem
    print("\n=== Example 2: Logical Problem ===\n")
    logic_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant that solves logical problems step by step.
        First, identify the key information.
        Then, analyze the relationships between different elements.
        Finally, draw a conclusion.
        
        Format your response as:
        Thought: [your step-by-step reasoning]
        Answer: [final answer]"""),
        ("human", """Three friends are sitting in a row. Alice is not next to Bob.
        Charlie is not at either end. Who is in the middle?""")
    ])
    
    chain = logic_prompt | llm
    response = chain.invoke({})
    print(response.content)
    
    # Example 3: Code Analysis
    print("\n=== Example 3: Code Analysis ===\n")
    code_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant that analyzes code step by step.
        First, identify the key components and their relationships.
        Then, analyze potential issues or improvements.
        Finally, provide recommendations.
        
        Format your response as:
        Thought: [your step-by-step analysis]
        Answer: [final recommendations]"""),
        ("human", """Analyze this code snippet:
        def calculate_average(numbers):
            total = 0
            for num in numbers:
                total += num
            return total / len(numbers)
        
        What potential issues might this code have?""")
    ])
    
    chain = code_prompt | llm
    response = chain.invoke({})
    print(response.content)

def demonstrate_chain_of_thought_with_few_shot():
    """Demonstrate chain of thought prompting with few-shot examples."""
    print("\nChain of Thought with Few-Shot Examples\n")
    
    # Use GPT-4o for better reasoning
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant that solves problems step by step.
        First, think about the problem carefully.
        Then, explain your reasoning.
        Finally, provide the answer.
        
        Here are some examples:
        
        Problem: If a rectangle has a length of 8 units and a width of 6 units, what is its area?
        Thought: Let me solve this step by step:
        1. The area of a rectangle is calculated by multiplying its length by its width
        2. The length is 8 units
        3. The width is 6 units
        4. Therefore, area = 8 × 6 = 48 square units
        Answer: The area is 48 square units
        
        Problem: A train travels 120 miles in 2 hours. What is its average speed?
        Thought: Let me solve this step by step:
        1. Average speed is calculated by dividing total distance by total time
        2. Total distance is 120 miles
        3. Total time is 2 hours
        4. Therefore, speed = 120 ÷ 2 = 60 miles per hour
        Answer: The average speed is 60 miles per hour
        
        Now solve this problem following the same format:"""),
        ("human", "If a triangle has angles of 45°, 45°, and 90°, what is the ratio of its sides?")
    ])
    
    chain = prompt | llm
    response = chain.invoke({})
    print(response.content)

def main():
    demonstrate_chain_of_thought()
    demonstrate_chain_of_thought_with_few_shot()

if __name__ == "__main__":
    main() 