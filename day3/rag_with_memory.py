import streamlit as st
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.chains import ConversationChain
import os
from dotenv import load_dotenv
import tempfile

# Load environment variables
load_dotenv()

# Initialize session state
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None
if 'current_file' not in st.session_state:
    st.session_state.current_file = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'buffer_memory' not in st.session_state:
    st.session_state.buffer_memory = ConversationBufferMemory(
        return_messages=True,
        memory_key="chat_history"
    )
if 'summary_memory' not in st.session_state:
    st.session_state.summary_memory = ConversationSummaryMemory(
        llm=ChatOpenAI(temperature=0),
        return_messages=True,
        memory_key="summary"
    )

def create_vector_store(file_path, chunk_size=1000, chunk_overlap=200):
    """Create a FAISS vector store from a PDF file."""
    try:
        with st.spinner('Loading PDF...'):
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
            chunks = text_splitter.split_text(full_text)
            st.success(f'Created {len(chunks)} chunks')
            
            # Initialize embeddings
            with st.spinner('Creating embeddings...'):
                embeddings = OpenAIEmbeddings()
                
                # Create vector store
                vector_store = FAISS.from_texts(chunks, embeddings)
                st.success('Vector store created successfully!')
                
                return vector_store, chunks
                
    except Exception as e:
        st.error(f"Error creating vector store: {str(e)}")
        return None, None

def get_relevant_chunks(vector_store, query, k=3):
    """Retrieve relevant chunks from the vector store."""
    try:
        results = vector_store.similarity_search_with_score(query, k=k)
        chunks = [doc.page_content for doc, _ in results]
        return chunks, results
    except Exception as e:
        st.error(f"Error retrieving chunks: {str(e)}")
        return None, None

def create_prompt(query, chunks, chat_history=None, summary=None):
    """Create a prompt for the LLM using the query and relevant chunks."""
    context = "\n\n".join(chunks)
    
    # Create the system message with context and memory
    system_message = """You are a helpful assistant that answers questions based on the provided context.
    Use the context to answer the question accurately and concisely.
    If the context doesn't contain enough information to answer the question, say so.
    Do not make up information that isn't in the context.
    
    Context:
    {context}
    
    {summary}
    """
    
    # Format the system message
    formatted_system = system_message.format(
        context=context,
        summary=f"Summary of previous conversation:\n{summary}" if summary else ""
    )
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", formatted_system),
        ("human", "{input}")
    ])
    
    # Format the prompt with chat history if available
    if chat_history:
        return prompt.format_messages(
            input=query,
            chat_history=chat_history
        )
    else:
        return prompt.format_messages(input=query)

def generate_answer(prompt, llm):
    """Generate an answer using the LLM."""
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        st.error(f"Error generating answer: {str(e)}")
        return None

def answer_question(vector_store, query, k=3):
    """Answer a question using the RAG system with memory."""
    try:
        # Get relevant chunks
        chunks, results = get_relevant_chunks(vector_store, query, k)
        
        if not chunks:
            return "Sorry, I couldn't find relevant information to answer your question.", None, None
        
        # Get chat history and summary from memory
        chat_history = st.session_state.buffer_memory.load_memory_variables({}).get("chat_history", [])
        summary = st.session_state.summary_memory.load_memory_variables({}).get("summary", "")
        
        # Create the prompt
        prompt = create_prompt(query, chunks, chat_history, summary)
        
        # Initialize the LLM
        llm = ChatOpenAI(temperature=0)
        
        # Generate the answer
        answer = generate_answer(prompt, llm)
        
        if answer:
            # Update both memories
            st.session_state.buffer_memory.save_context({"input": query}, {"output": answer})
            st.session_state.summary_memory.save_context({"input": query}, {"output": answer})
        
        return answer, chunks, results
        
    except Exception as e:
        st.error(f"Error answering question: {str(e)}")
        return "Sorry, I encountered an error while trying to answer your question.", None, None

# Streamlit UI
st.title("📚 Document Q&A with RAG and Memory")
st.write("Upload a PDF document and ask questions about its content. The system maintains both short-term and long-term memory of the conversation.")

# File upload
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

# Parameters in sidebar
with st.sidebar:
    st.header("Parameters")
    chunk_size = st.slider("Chunk Size", min_value=500, max_value=5000, value=1000, step=100)
    chunk_overlap = st.slider("Chunk Overlap", min_value=0, max_value=500, value=200, step=50)
    num_chunks = st.slider("Number of Chunks to Retrieve", min_value=1, max_value=5, value=3)
    
    # Display long-term memory (summary) in sidebar
    st.header("Long-term Memory")
    summary = st.session_state.summary_memory.load_memory_variables({}).get("summary", "")
    if summary:
        st.text_area("Conversation Summary", value=summary, height=200)
    else:
        st.info("No conversation history yet.")

# Process uploaded file
if uploaded_file is not None:
    # Save uploaded file to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name
    
    # Create vector store if file is new
    if st.session_state.current_file != uploaded_file.name:
        st.session_state.vector_store, chunks = create_vector_store(
            tmp_file_path, 
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap
        )
        st.session_state.current_file = uploaded_file.name

# Question input and answer display
if st.session_state.vector_store:
    # Create a single text input
    question = st.text_input("Ask a question about the document:", key="question_input")
    
    if question:
        # Get answer
        answer, retrieved_chunks, results = answer_question(
            st.session_state.vector_store, 
            question, 
            k=num_chunks
        )
        
        # Display answer in a textbox
        st.text_area("Answer:", value=answer, height=200)
        
        # Display relevant chunks in an expander
        if retrieved_chunks:
            with st.expander("View Relevant Chunks"):
                for j, (chunk, (_, score)) in enumerate(zip(retrieved_chunks, results)):
                    st.markdown(f"**Chunk {j+1}** (Similarity Score: {score:.4f})")
                    st.markdown("---")
                    st.markdown(chunk)
                    st.markdown("---")
    
    # Display chat history
    st.header("Chat History")
    chat_history = st.session_state.buffer_memory.load_memory_variables({}).get("chat_history", [])
    if chat_history:
        for message in chat_history:
            if message.type == "human":
                st.markdown(f"**You:** {message.content}")
            else:
                st.markdown(f"**Assistant:** {message.content}")
    else:
        st.info("No messages in the chat history yet.") 