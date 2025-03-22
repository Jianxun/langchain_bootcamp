import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import OpenAI
import streamlit as st
from dotenv import load_dotenv
import tempfile

# Load environment variables
load_dotenv()

# Initialize Streamlit page configuration
st.set_page_config(
    page_title="QA Chatbot",
    page_icon="📚",
    layout="wide"
)

# Initialize session state for vector store
if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None

def process_pdf(pdf_file):
    """Process uploaded PDF file and create vector store."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(pdf_file.getvalue())
        tmp_file_path = tmp_file.name
    
    try:
        # Load PDF
        loader = PyPDFLoader(file_path=tmp_file_path)
        doc = loader.load()

        # Split text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        text = text_splitter.split_documents(documents=doc)

        # Create embeddings
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_documents(text, embeddings)
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        return vectorstore
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return None

def get_response(query, chat_history):
    """Get response from the QA chain."""
    if not st.session_state.vectorstore:
        return {"answer": "Please upload a PDF file first."}
    
    qa = ConversationalRetrievalChain.from_llm(
        llm=OpenAI(),
        retriever=st.session_state.vectorstore.as_retriever()
    )
    
    return qa({"question": query, "chat_history": chat_history})

# Main UI
st.title("📚 QA Chatbot")

# File uploader
uploaded_file = st.file_uploader("Upload a PDF file", type=['pdf'])

if uploaded_file and not st.session_state.vectorstore:
    with st.spinner("Processing PDF..."):
        st.session_state.vectorstore = process_pdf(uploaded_file)
        if st.session_state.vectorstore:
            st.success("PDF processed successfully!")

# Initialize chat history
if "user_prompt_history" not in st.session_state:
    st.session_state["user_prompt_history"] = []
if "chat_answers_history" not in st.session_state:
    st.session_state["chat_answers_history"] = []
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# Chat input
prompt = st.chat_input("Ask a question about your document")

if prompt:
    with st.spinner("Generating answer..."):
        output = get_response(prompt, st.session_state["chat_history"])
        
        # Store the conversation
        st.session_state["chat_answers_history"].append(output['answer'])
        st.session_state["user_prompt_history"].append(prompt)
        st.session_state["chat_history"].append((prompt, output['answer']))

# Display chat history
if st.session_state["chat_answers_history"]:
    for i, j in zip(st.session_state["chat_answers_history"], st.session_state["user_prompt_history"]):
        with st.chat_message("user"):
            st.write(j)
        with st.chat_message("assistant"):
            st.write(i)