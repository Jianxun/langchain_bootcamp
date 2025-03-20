import os
from typing import List, Dict, Any
import asyncio
from datetime import datetime
import logging
from pathlib import Path
import json
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import time

from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredFileLoader,
    DirectoryLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import io

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ProcessingConfig:
    """Configuration for document processing"""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    batch_size: int = 100
    max_workers: int = 4
    rate_limit_tokens: int = 1_000_000
    rate_limit_period: int = 60  # seconds

class RateLimitHandler:
    """Handle rate limiting for API calls"""
    def __init__(self, tokens_per_minute: int, period: int):
        self.tokens_per_minute = tokens_per_minute
        self.period = period
        self.current_tokens = 0
        self.last_reset = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self, tokens: int):
        async with self.lock:
            current_time = time.time()
            if current_time - self.last_reset >= self.period:
                self.current_tokens = 0
                self.last_reset = current_time
            
            if self.current_tokens + tokens > self.tokens_per_minute:
                wait_time = self.period - (current_time - self.last_reset)
                logger.info(f"Rate limit reached. Waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
                self.current_tokens = 0
                self.last_reset = time.time()
            
            self.current_tokens += tokens

class DocumentProcessor:
    """Process documents for RAG implementation"""
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.rate_limiter = RateLimitHandler(
            config.rate_limit_tokens,
            config.rate_limit_period
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            length_function=len
        )
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = None

    async def process_document(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a single document"""
        try:
            # Load document based on file type
            if file_path.endswith('.pdf'):
                loader = PyPDFLoader(file_path)
            else:
                loader = UnstructuredFileLoader(file_path)
            
            documents = loader.load()
            
            # Extract text and metadata
            processed_docs = []
            for doc in documents:
                # Split into chunks
                chunks = self.text_splitter.split_text(doc.page_content)
                
                # Process each chunk
                for chunk in chunks:
                    processed_docs.append({
                        'text': chunk,
                        'metadata': {
                            'source': file_path,
                            'page': doc.metadata.get('page', 0),
                            'timestamp': datetime.now().isoformat()
                        }
                    })
            
            return processed_docs
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            return []

    async def process_directory(self, directory: str) -> None:
        """Process all documents in a directory"""
        try:
            # Load all documents from directory
            loader = DirectoryLoader(
                directory,
                glob="**/*.*",
                loader_cls=UnstructuredFileLoader
            )
            documents = loader.load()
            
            # Process documents in batches
            all_chunks = []
            for i in range(0, len(documents), self.config.batch_size):
                batch = documents[i:i + self.config.batch_size]
                tasks = [self.process_document(doc.metadata['source']) for doc in batch]
                results = await asyncio.gather(*tasks)
                
                # Flatten results
                for chunks in results:
                    all_chunks.extend(chunks)
                
                # Update progress
                logger.info(f"Processed {min(i + self.config.batch_size, len(documents))}/{len(documents)} documents")
            
            # Create embeddings and store in vector database
            if all_chunks:
                texts = [chunk['text'] for chunk in all_chunks]
                metadatas = [chunk['metadata'] for chunk in all_chunks]
                
                # Create embeddings with rate limiting
                await self.rate_limiter.acquire(len(texts))
                embeddings = await self.embeddings.aembed_documents(texts)
                
                # Create vector store
                self.vector_store = FAISS.from_texts(
                    texts=texts,
                    embedding=self.embeddings,
                    metadatas=metadatas
                )
                
                logger.info(f"Created vector store with {len(texts)} documents")
            
        except Exception as e:
            logger.error(f"Error processing directory {directory}: {str(e)}")

    async def process_multi_modal_document(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a document containing both text and images"""
        try:
            if file_path.endswith('.pdf'):
                # Convert PDF to images
                images = convert_from_path(file_path)
                
                processed_docs = []
                for i, image in enumerate(images):
                    # Extract text from image
                    text = pytesseract.image_to_string(image)
                    
                    # Split text into chunks
                    chunks = self.text_splitter.split_text(text)
                    
                    # Process each chunk
                    for chunk in chunks:
                        processed_docs.append({
                            'text': chunk,
                            'metadata': {
                                'source': file_path,
                                'page': i + 1,
                                'type': 'image',
                                'timestamp': datetime.now().isoformat()
                            }
                        })
                
                return processed_docs
                
            else:
                # Process as regular document
                return await self.process_document(file_path)
                
        except Exception as e:
            logger.error(f"Error processing multi-modal document {file_path}: {str(e)}")
            return []

    def save_vector_store(self, path: str) -> None:
        """Save the vector store to disk"""
        if self.vector_store:
            self.vector_store.save_local(path)
            logger.info(f"Saved vector store to {path}")

    def load_vector_store(self, path: str) -> None:
        """Load the vector store from disk"""
        if os.path.exists(path):
            self.vector_store = FAISS.load_local(path, self.embeddings)
            logger.info(f"Loaded vector store from {path}")

async def main():
    # Example usage
    config = ProcessingConfig()
    processor = DocumentProcessor(config)
    
    # Process research papers
    research_dir = "data/research_papers"
    await processor.process_directory(research_dir)
    processor.save_vector_store("vector_store/research")
    
    # Process multi-modal documents
    multi_modal_dir = "data/multi_modal"
    await processor.process_directory(multi_modal_dir)
    processor.save_vector_store("vector_store/multi_modal")

if __name__ == "__main__":
    asyncio.run(main()) 