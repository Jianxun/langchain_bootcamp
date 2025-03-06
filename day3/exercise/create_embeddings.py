from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import os
from dotenv import load_dotenv
import numpy as np

# Load environment variables
load_dotenv()

def create_embeddings(file_path, chunk_size=1000, chunk_overlap=200):
    """
    Load a PDF, split it into chunks, and create embeddings for each chunk.
    
    Args:
        file_path (str): Path to the PDF file
        chunk_size (int): Size of each chunk in characters
        chunk_overlap (int): Number of characters to overlap between chunks
        
    Returns:
        dict: Dictionary containing chunks and their embeddings
    """
    try:
        # Load the PDF
        print(f"Loading PDF from: {file_path}")
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        # Combine all pages into a single text
        full_text = "\n".join(doc.page_content for doc in documents)
        
        # Initialize text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Split the text into chunks
        print("\nSplitting text into chunks...")
        chunks = text_splitter.split_text(full_text)
        print(f"Created {len(chunks)} chunks")
        
        # Initialize embeddings
        print("\nCreating embeddings...")
        embeddings = OpenAIEmbeddings()
        
        # Create embeddings for each chunk
        chunk_embeddings = []
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}")
            embedding = embeddings.embed_query(chunk)
            chunk_embeddings.append(embedding)
        
        # Print some statistics about the embeddings
        print("\nEmbedding Statistics:")
        print(f"Number of embeddings: {len(chunk_embeddings)}")
        print(f"Embedding dimension: {len(chunk_embeddings[0])}")
        
        # Calculate and print average similarity between consecutive chunks
        similarities = []
        for i in range(len(chunk_embeddings) - 1):
            similarity = np.dot(chunk_embeddings[i], chunk_embeddings[i + 1])
            similarities.append(similarity)
        
        print(f"\nAverage similarity between consecutive chunks: {np.mean(similarities):.4f}")
        
        return {
            "chunks": chunks,
            "embeddings": chunk_embeddings
        }
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return None

if __name__ == "__main__":
    # PDF file path
    pdf_path = "day3/documents/ISSCC2025CFP.pdf"
    
    # Create embeddings
    result = create_embeddings(pdf_path)
    
    if result:
        print("\nEmbeddings created successfully!") 