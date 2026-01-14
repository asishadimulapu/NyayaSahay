# Indian Law RAG Chatbot - FAISS Vector Store
"""
FAISS vector store management for efficient similarity search.

Viva Explanation:
- FAISS (Facebook AI Similarity Search) enables fast vector search
- Supports billions of vectors with millisecond latency
- Uses approximate nearest neighbor (ANN) algorithms
- IndexFlatL2 uses exact L2 (Euclidean) distance for small datasets
"""

import os
from pathlib import Path
from typing import List, Optional, Tuple
import logging

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.config import settings
from app.core.embeddings import get_embedding_model

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """
    Manager class for FAISS vector store operations.
    
    Viva Explanation:
    - Handles creation, loading, and saving of FAISS index
    - Provides similarity search interface
    - Manages index persistence for production use
    """
    
    def __init__(self, index_path: Optional[str] = None):
        """
        Initialize the vector store manager.
        
        Args:
            index_path: Path to store/load FAISS index
        """
        self.index_path = index_path or settings.faiss_index_path
        self._vector_store: Optional[FAISS] = None
        self._embeddings = None
    
    @property
    def embeddings(self):
        """Lazy load embeddings model."""
        if self._embeddings is None:
            self._embeddings = get_embedding_model()
        return self._embeddings
    
    @property
    def vector_store(self) -> Optional[FAISS]:
        """Get the loaded vector store."""
        return self._vector_store
    
    def create_from_documents(
        self, 
        documents: List[Document],
        save: bool = True
    ) -> FAISS:
        """
        Create a new FAISS index from documents.
        
        Args:
            documents: List of LangChain Document objects
            save: Whether to save the index to disk
            
        Returns:
            FAISS: Created vector store
            
        Viva Explanation:
        - Documents are converted to embeddings
        - Embeddings are indexed for fast retrieval
        - Metadata is preserved for citations
        """
        if not documents:
            raise ValueError("No documents provided for indexing")
        
        logger.info(f"Creating FAISS index from {len(documents)} documents")
        
        # Create FAISS index
        self._vector_store = FAISS.from_documents(
            documents=documents,
            embedding=self.embeddings
        )
        
        logger.info("FAISS index created successfully")
        
        # Save to disk if requested
        if save:
            self.save()
        
        return self._vector_store
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add new documents to existing index.
        
        Args:
            documents: Documents to add
        """
        if self._vector_store is None:
            raise ValueError("Vector store not initialized. Call create_from_documents or load first.")
        
        logger.info(f"Adding {len(documents)} documents to index")
        self._vector_store.add_documents(documents)
    
    def load(self) -> FAISS:
        """
        Load FAISS index from disk.
        
        Returns:
            FAISS: Loaded vector store
            
        Raises:
            FileNotFoundError: If index doesn't exist
        """
        index_path = Path(self.index_path)
        
        if not index_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found at {self.index_path}. "
                "Run the data pipeline first to create the index."
            )
        
        logger.info(f"Loading FAISS index from {self.index_path}")
        
        self._vector_store = FAISS.load_local(
            folder_path=str(index_path),
            embeddings=self.embeddings,
            allow_dangerous_deserialization=True  # Required for loading
        )
        
        logger.info("FAISS index loaded successfully")
        return self._vector_store
    
    def save(self) -> None:
        """
        Save FAISS index to disk.
        
        Viva Explanation:
        - Persists index for production use
        - Avoids re-embedding on restart
        - Saves both index and metadata
        """
        if self._vector_store is None:
            raise ValueError("No vector store to save")
        
        # Create directory if needed
        index_path = Path(self.index_path)
        index_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Saving FAISS index to {self.index_path}")
        self._vector_store.save_local(str(index_path))
        logger.info("FAISS index saved successfully")
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 5
    ) -> List[Document]:
        """
        Perform similarity search on the vector store.
        
        Args:
            query: Search query
            k: Number of results to return (top-k)
            
        Returns:
            List[Document]: Most similar documents
            
        Viva Explanation:
        - Query is embedded using same model as documents
        - FAISS finds k-nearest neighbors in vector space
        - Returns documents ordered by similarity
        """
        if self._vector_store is None:
            raise ValueError("Vector store not loaded")
        
        logger.debug(f"Searching for: {query[:100]}...")
        
        results = self._vector_store.similarity_search(query, k=k)
        
        logger.debug(f"Found {len(results)} results")
        return results
    
    def similarity_search_with_score(
        self, 
        query: str, 
        k: int = 5
    ) -> List[Tuple[Document, float]]:
        """
        Perform similarity search with relevance scores.
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List[Tuple[Document, float]]: Documents with scores
            
        Viva Explanation:
        - Score indicates similarity (lower = more similar for L2)
        - Useful for filtering low-confidence results
        - Can set threshold to reject irrelevant documents
        """
        if self._vector_store is None:
            raise ValueError("Vector store not loaded")
        
        results = self._vector_store.similarity_search_with_score(query, k=k)
        return results
    
    def is_loaded(self) -> bool:
        """Check if vector store is loaded."""
        return self._vector_store is not None
    
    def get_document_count(self) -> int:
        """Get the number of documents in the index."""
        if self._vector_store is None:
            return 0
        return len(self._vector_store.docstore._dict)


# Global vector store manager instance
vector_store_manager = VectorStoreManager()


def load_vector_store() -> VectorStoreManager:
    """
    Load the global vector store.
    
    Returns:
        VectorStoreManager: Loaded manager instance
    """
    if not vector_store_manager.is_loaded():
        vector_store_manager.load()
    return vector_store_manager


def get_vector_store() -> VectorStoreManager:
    """
    Get the vector store manager (for dependency injection).
    
    Returns:
        VectorStoreManager: Global manager instance
    """
    return vector_store_manager
