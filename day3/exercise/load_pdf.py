from langchain_community.document_loaders import PyPDFLoader
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_pdf(file_path):
    """
    Load a PDF file and return its content.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        list: List of Document objects containing the PDF content
    """
    try:
        # Create a PDF loader
        loader = PyPDFLoader(file_path)
        
        # Load the PDF
        print(f"Loading PDF from: {file_path}")
        documents = loader.load()
        
        # Print basic information about the loaded documents
        print(f"\nNumber of pages: {len(documents)}")
        print("\nFirst page preview:")
        print("-" * 50)
        print(documents[0].page_content[:500] + "...")
        
        return documents
        
    except Exception as e:
        print(f"Error loading PDF: {str(e)}")
        return None

if __name__ == "__main__":
    # Replace with your PDF file path
    pdf_path = "day3/documents/ISSCC2025CFP.pdf"
    
    # Load the PDF
    documents = load_pdf(pdf_path)
    
    if documents:
        print("\nPDF loaded successfully!") 