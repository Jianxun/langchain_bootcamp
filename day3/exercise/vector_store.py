from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_vector_store(file_path, chunk_size=3000, chunk_overlap=200):
    """
    Create a FAISS vector store from a PDF file.
    
    Args:
        file_path (str): Path to the PDF file
        chunk_size (int): Size of each chunk in characters
        chunk_overlap (int): Number of characters to overlap between chunks
        
    Returns:
        FAISS: Vector store containing the document chunks and their embeddings
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
        
        # Create vector store
        print("\nCreating vector store...")
        vector_store = FAISS.from_texts(chunks, embeddings)
        
        # Print some statistics
        print(f"\nVector store created with {len(chunks)} documents")
        
        return vector_store
        
    except Exception as e:
        print(f"Error creating vector store: {str(e)}")
        return None

def query_vector_store(vector_store, query, k=3):
    """
    Query the vector store to find relevant chunks.
    
    Args:
        vector_store (FAISS): The vector store to query
        query (str): The query text
        k (int): Number of results to return
        
    Returns:
        list: List of relevant chunks and their scores
    """
    try:
        # Perform similarity search
        results = vector_store.similarity_search_with_score(query, k=k)
        
        print(f"\nQuery: {query}")
        print("\nRelevant chunks:")
        for i, (doc, score) in enumerate(results, 1):
            print(f"\n{i}. Score: {score:.4f}")
            print("-" * 50)
            print(doc.page_content)
            print("-" * 50)
        
        return results
        
    except Exception as e:
        print(f"Error querying vector store: {str(e)}")
        return None

if __name__ == "__main__":
    # PDF file path
    pdf_path = "day3/documents/ISSCC2025CFP.pdf"
    
    # Create vector store
    vector_store = create_vector_store(pdf_path)
    
    if vector_store:
        print("\nVector store created successfully!")
        
        # Example queries
        queries = [
            "What are the key dates for paper submission?",
            "What are the main topics of interest?",
            "What is the format for paper submission?"
        ]
        
        print("\nTesting queries...")
        for query in queries:
            query_vector_store(vector_store, query) 