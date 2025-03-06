from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
    MarkdownTextSplitter
)
from langchain_community.document_loaders import PyPDFLoader
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_and_split_pdf(file_path, chunk_size=1000, chunk_overlap=200):
    """
    Load a PDF file and split it into chunks using different strategies.
    
    Args:
        file_path (str): Path to the PDF file
        chunk_size (int): Size of each chunk in characters
        chunk_overlap (int): Number of characters to overlap between chunks
        
    Returns:
        dict: Dictionary containing chunks from different splitting strategies
    """
    try:
        # Load the PDF
        print(f"Loading PDF from: {file_path}")
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        # Combine all pages into a single text
        full_text = "\n".join(doc.page_content for doc in documents)
        
        # Initialize different text splitters
        recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        character_splitter = CharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separator="\n"
        )
        
        # Split the text using different strategies
        print("\nSplitting text using different strategies...")
        
        # Recursive splitting (recommended for most cases)
        recursive_chunks = recursive_splitter.split_text(full_text)
        print(f"\nRecursive splitting produced {len(recursive_chunks)} chunks")
        print("First chunk preview:")
        print("-" * 50)
        print(recursive_chunks[0][:200] + "...")
        
        # Character splitting
        character_chunks = character_splitter.split_text(full_text)
        print(f"\nCharacter splitting produced {len(character_chunks)} chunks")
        print("First chunk preview:")
        print("-" * 50)
        print(character_chunks[0][:200] + "...")
        
        return {
            "recursive_chunks": recursive_chunks,
            "character_chunks": character_chunks
        }
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return None

if __name__ == "__main__":
    # PDF file path
    pdf_path = "day3/documents/ISSCC2025CFP.pdf"
    
    # Load and split the PDF
    chunks = load_and_split_pdf(pdf_path)
    
    if chunks:
        print("\nText splitting completed successfully!") 

    for chunk in chunks["recursive_chunks"]:
        print(chunk)
        print("-" * 100)
    