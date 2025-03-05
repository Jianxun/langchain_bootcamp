from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import os
from dotenv import load_dotenv

load_dotenv()

def summarize_document(text: str, style: str):
    """Summarize a document using different styles."""
    
    llm = ChatOpenAI(temperature=0.7, model="gpt-4o")

    prompt_narrative = ChatPromptTemplate.from_messages([
        ("system", "You are a technical analyst that helps the user to summarize materials into a single paragraph that can be used in another writing as background information. Output plain text in a narrative tone."),
        ("human", "Summarize the following {text}.")
    ])

    prompt_bullet_points = ChatPromptTemplate.from_messages([
        ("system", "You are a technical analyst that helps the user to summarize documnets into concise bullet points for quick reference. Output in a structured markdown format."),
        ("human", "Summarize the following {text}.")
    ])
    
    prompt_structured_data = ChatPromptTemplate.from_messages([
        ("system", "You are a technical analyst that helps the user to summarize materials as into structured data in JSON format."),
        ("human", "Summarize the following {text}.")
    ])
    
    chain_narrative = prompt_narrative | llm
    chain_bullet_points = prompt_bullet_points | llm
    chain_structured_data = prompt_structured_data | llm


        
    if style == "bullet_points":
        print("-" * 100)
        print(f"Summarizing document using bullet points style...")
        summary = chain_bullet_points.invoke({"text": text})
        print(summary.content)
    elif style == "structured_data":
        print("-" * 100)
        print(f"Summarizing document using structured data style...")   
        summary = chain_structured_data.invoke({"text": text})
        print(summary.content)
    else:
        print("-" * 100)
        print(f"Summarizing document using narrative style...")
        summary = chain_narrative.invoke({"text": text})
        print(summary.content)

    return summary

if __name__ == "__main__":
    document_path = "day2/finite_state_machine.txt"
    with open(document_path, 'r') as file:
        text = file.read()
    styles = ["", "bullet_points", "structured_data"]
    for style in styles:

        summarize_document(text, style)
        print("\n")

