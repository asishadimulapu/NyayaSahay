# Indian Law RAG Chatbot - FAISS Index Creation
"""
Create FAISS vector index from the Indian law dataset.
This is a one-time setup script that generates embeddings and saves the index.

Viva Explanation:
- Loads documents from the dataset
- Splits into chunks using RecursiveCharacterTextSplitter
- Generates embeddings using configured provider (OpenAI/Gemini)
- Creates and saves FAISS index for similarity search
"""

import sys
import os
from pathlib import Path
from typing import List
import logging
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up environment
from dotenv import load_dotenv
load_dotenv(project_root / ".env")

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.config import settings
from app.core.vector_store import VectorStoreManager
from scripts.load_dataset import load_indian_law_dataset, create_sample_documents

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s"
)
logger = logging.getLogger(__name__)


def chunk_documents(documents: List[Document]) -> List[Document]:
    """
    Split documents into smaller chunks for better retrieval.
    
    Args:
        documents: List of full documents
        
    Returns:
        List[Document]: Chunked documents
        
    Viva Explanation:
    - RecursiveCharacterTextSplitter tries to split on natural boundaries
    - Separators: paragraphs > sentences > words
    - Chunk size 800 chars is optimal for legal text
    - 150 char overlap ensures context is preserved across chunks
    """
    logger.info(f"Chunking {len(documents)} documents...")
    logger.info(f"Chunk size: {settings.chunk_size}, Overlap: {settings.chunk_overlap}")
    
    # Create splitter with configured settings
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", "; ", ", ", " ", ""],
        length_function=len
    )
    
    # Split documents
    chunks = splitter.split_documents(documents)
    
    logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
    
    # Add chunk index to metadata
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i
    
    return chunks


def create_faiss_index(
    documents: List[Document],
    index_path: str = None
) -> None:
    """
    Create and save FAISS index from documents.
    
    Args:
        documents: Documents to index
        index_path: Path to save index (optional)
        
    Viva Explanation:
    - Embeddings are generated for each chunk
    - FAISS IndexFlatL2 uses exact L2 distance
    - Index is saved to disk for fast loading
    """
    index_path = index_path or settings.faiss_index_path
    
    logger.info("=" * 60)
    logger.info("Creating FAISS Index")
    logger.info("=" * 60)
    logger.info(f"Documents to index: {len(documents)}")
    logger.info(f"Index path: {index_path}")
    logger.info(f"Embedding provider: {settings.embedding_provider}")
    
    # Validate API key for embeddings (HuggingFace doesn't need one!)
    if settings.embedding_provider == "openai" and not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required for embeddings. Set it in .env file.")
    if settings.embedding_provider == "gemini" and not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY is required for embeddings. Set it in .env file.")
    if settings.embedding_provider == "huggingface":
        logger.info("Using HuggingFace embeddings (FREE, no API key needed!)")
    
    start_time = time.time()
    
    # Create vector store manager
    manager = VectorStoreManager(index_path)
    
    # Create index from documents
    logger.info("Generating embeddings and creating FAISS index...")
    logger.info("This may take several minutes depending on dataset size...")
    
    manager.create_from_documents(documents, save=True)
    
    duration = time.time() - start_time
    
    logger.info("=" * 60)
    logger.info("Index Creation Complete!")
    logger.info("=" * 60)
    logger.info(f"Total documents indexed: {manager.get_document_count()}")
    logger.info(f"Time taken: {duration:.2f} seconds")
    logger.info(f"Index saved to: {index_path}")


def main():
    """Main function to create the FAISS index."""
    print("\n" + "=" * 60)
    print("Indian Law RAG Chatbot - FAISS Index Creation")
    print("=" * 60 + "\n")
    
    # Step 1: Load dataset
    print("Step 1: Loading dataset...")
    try:
        documents = load_indian_law_dataset()
    except Exception as e:
        logger.warning(f"Dataset loading failed: {e}")
        print("\nUsing sample documents for demonstration...")
        documents = create_sample_documents()
    
    if not documents:
        logger.error("No documents to index!")
        return
    
    print(f"Loaded {len(documents)} documents\n")
    
    # Step 2: Chunk documents
    print("Step 2: Chunking documents...")
    chunks = chunk_documents(documents)
    print(f"Created {len(chunks)} chunks\n")
    
    # Step 3: Create FAISS index
    print("Step 3: Creating FAISS index...")
    print("This will generate embeddings for all chunks.")
    print("Please wait...\n")
    
    try:
        create_faiss_index(chunks)
        print("\n✓ FAISS index created successfully!")
        print(f"✓ Index saved to: {settings.faiss_index_path}")
        print("\nYou can now start the application with: python run.py")
    except Exception as e:
        logger.error(f"Failed to create index: {e}")
        print(f"\n✗ Error: {e}")
        print("\nMake sure you have set your API key in the .env file:")
        print("  - GOOGLE_API_KEY for Gemini")
        print("  - OPENAI_API_KEY for OpenAI")


if __name__ == "__main__":
    main()
