# Day 3: Retrieval Augmented Generation (RAG)

## Overview
Day 3 focuses on implementing a Retrieval Augmented Generation (RAG) system, which combines document retrieval with language models to provide accurate, context-aware answers to questions about documents.

## Key Components

### 1. Document Processing
- **PDF Loading**: Using `PyPDFLoader` from LangChain to load and process PDF documents
- **Text Splitting**: Implementing `RecursiveCharacterTextSplitter` for intelligent text chunking
  - Configurable chunk size and overlap
  - Respects natural text boundaries
  - Maintains context through overlapping chunks

### 2. Vector Store
- **FAISS Integration**: Using FAISS for efficient similarity search
- **Embeddings**: Leveraging OpenAI's embedding model to convert text into vector representations
- **Similarity Search**: Implementing semantic search to find relevant document chunks

### 3. RAG System
- **Context Retrieval**: Finding relevant document chunks based on user queries
- **Prompt Engineering**: Creating structured prompts that combine context with questions
- **Answer Generation**: Using GPT models to generate accurate, context-aware responses

## Project: Document Q&A System

### Features
- PDF document upload and processing
- Configurable text chunking parameters
- Interactive question-answering interface
- Display of relevant source chunks with similarity scores
- Streamlit-based user interface

### Technical Implementation
1. **Document Processing Pipeline**:
   ```python
   # Load and split document
   loader = PyPDFLoader(file_path)
   documents = loader.load()
   chunks = text_splitter.split_text(full_text)
   ```

2. **Vector Store Creation**:
   ```python
   embeddings = OpenAIEmbeddings()
   vector_store = FAISS.from_texts(chunks, embeddings)
   ```

3. **Question Answering**:
   ```python
   # Retrieve relevant chunks
   chunks, results = vector_store.similarity_search_with_score(query, k=3)
   
   # Generate answer
   prompt = create_prompt(query, chunks)
   answer = generate_answer(prompt)
   ```

### User Interface
- File upload for PDF documents
- Parameter controls in sidebar:
  - Chunk size
  - Chunk overlap
  - Number of chunks to retrieve
- Question input field
- Answer display in text area
- Expandable view of relevant source chunks

## Learning Outcomes
1. Understanding RAG architecture and components
2. Implementing document processing pipelines
3. Working with vector stores and embeddings
4. Building interactive document Q&A systems
5. Configuring and optimizing text chunking

## Next Steps
1. Enhance the system with:
   - Support for more document types
   - Advanced chunking strategies
   - Different embedding models
   - Alternative vector stores
2. Improve the interface with:
   - Document preview
   - Answer highlighting
   - Source citation
   - Export functionality

## Running the Application
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   - Create a `.env` file with your OpenAI API key:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

3. Run the Streamlit app:
   ```bash
   streamlit run day3/rag_app.py
   ```

4. Upload a PDF document and start asking questions! 