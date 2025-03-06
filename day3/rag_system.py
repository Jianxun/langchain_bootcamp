from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_vector_store(file_path, chunk_size=1000, chunk_overlap=200):
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

def get_relevant_chunks(vector_store, query, k=3):
    """
    Retrieve relevant chunks from the vector store.
    
    Args:
        vector_store (FAISS): The vector store to query
        query (str): The query text
        k (int): Number of chunks to retrieve
        
    Returns:
        list: List of relevant chunks
    """
    try:
        # Perform similarity search
        results = vector_store.similarity_search_with_score(query, k=k)
        
        # Extract just the chunks (without scores)
        chunks = [doc.page_content for doc, _ in results]
        
        return chunks
        
    except Exception as e:
        print(f"Error retrieving chunks: {str(e)}")
        return None

def create_prompt(query, chunks):
    """
    Create a prompt for the LLM using the query and relevant chunks.
    
    Args:
        query (str): The user's query
        chunks (list): List of relevant chunks
        
    Returns:
        str: Formatted prompt
    """
    # Create the context from chunks
    context = "\n\n".join(chunks)
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant that answers questions based on the provided context.
        Use the context to answer the question accurately and concisely.
        If the context doesn't contain enough information to answer the question, say so.
        Do not make up information that isn't in the context."""),
        ("human", """Context:
        {context}
        
        Question: {query}
        
        Answer:""")
    ])
    
    # Format the prompt
    formatted_prompt = prompt.format_messages(context=context, query=query)
    
    return formatted_prompt

def generate_answer(prompt):
    """
    Generate an answer using the LLM.
    
    Args:
        prompt (list): List of messages for the LLM
        
    Returns:
        str: Generated answer
    """
    try:
        # Initialize the LLM
        llm = ChatOpenAI(temperature=0)
        
        # Generate the answer
        response = llm.invoke(prompt)
        
        return response.content
        
    except Exception as e:
        print(f"Error generating answer: {str(e)}")
        return None

def answer_question(vector_store, query, k=3):
    """
    Answer a question using the RAG system.
    
    Args:
        vector_store (FAISS): The vector store to query
        query (str): The user's question
        k (int): Number of chunks to retrieve
        
    Returns:
        str: Generated answer
    """
    try:
        # Get relevant chunks
        print(f"\nRetrieving relevant chunks for query: {query}")
        chunks = get_relevant_chunks(vector_store, query, k)
        
        if not chunks:
            return "Sorry, I couldn't find relevant information to answer your question."
        
        # Create the prompt
        print("\nCreating prompt...")
        prompt = create_prompt(query, chunks)
        
        # Generate the answer
        print("\nGenerating answer...")
        answer = generate_answer(prompt)
        
        return answer
        
    except Exception as e:
        print(f"Error answering question: {str(e)}")
        return "Sorry, I encountered an error while trying to answer your question."

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
        
        print("\nTesting RAG system...")
        for query in queries:
            print(f"\nQuery: {query}")
            print("-" * 50)
            answer = answer_question(vector_store, query)
            print(answer)
            print("-" * 50) 