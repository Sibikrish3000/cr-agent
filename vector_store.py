"""
Vector Store Module using ChromaDB for Document RAG.

Provides document ingestion with chunking, embedding, and similarity search
functionality with configurable score thresholds.
"""

import os
from typing import List, Tuple, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


class VectorStoreManager:
    """Manages ChromaDB vector store for document embeddings."""
    
    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "documents",
        embedding_model: str = "BAAI/bge-small-en-v1.5",
        is_persistent: bool = True
    ):
        """
        Initialize Vector Store Manager.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
            collection_name: Name of the ChromaDB collection
            embedding_model: Sentence transformer model for embeddings
            is_persistent: Whether to use persistent storage or in-memory
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.is_persistent = is_persistent
        
        # Initialize ChromaDB client
        if is_persistent:
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
        else:
            # Ephemeral (in-memory) client
            self.client = chromadb.EphemeralClient(
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Document embeddings for RAG"}
        )
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Input text to chunk
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks in characters
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            
            # Only add non-empty chunks
            if chunk.strip():
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - chunk_overlap
            
            # Prevent infinite loop for very small texts
            if start >= text_length:
                break
        
        return chunks
    
    def ingest_document(
        self,
        document_text: str,
        document_id: str,
        metadata: Optional[dict] = None,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ) -> int:
        """
        Ingest document into vector store with chunking and embedding.
        
        Args:
            document_text: Full text of the document
            document_id: Unique identifier for the document
            metadata: Optional metadata to store with document
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks in characters
            
        Returns:
            Number of chunks created and stored
        """
        # Chunk the document
        chunks = self.chunk_text(document_text, chunk_size, chunk_overlap)
        
        if not chunks:
            return 0
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(
            chunks,
            convert_to_numpy=True,
            show_progress_bar=False
        ).tolist()
        
        # Prepare metadata for each chunk
        chunk_metadata = []
        for i in range(len(chunks)):
            meta = {
                "document_id": document_id,
                "chunk_index": i,
                "total_chunks": len(chunks)
            }
            if metadata:
                meta.update(metadata)
            chunk_metadata.append(meta)
        
        # Generate unique IDs for each chunk
        chunk_ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=chunk_metadata,
            ids=chunk_ids
        )
        
        return len(chunks)
    
    def similarity_search(
        self,
        query: str,
        top_k: int = 3,
        document_id: Optional[str] = None
    ) -> List[Tuple[str, float, dict]]:
        """
        Perform similarity search on vector store.
        
        Args:
            query: Query text to search for
            top_k: Number of top results to return
            document_id: Optional filter by specific document ID
            
        Returns:
            List of tuples: (chunk_text, similarity_score, metadata)
            Scores are between 0 and 1 (higher is more similar)
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(
            [query],
            convert_to_numpy=True,
            show_progress_bar=False
        ).tolist()[0]
        
        # Prepare where filter if document_id specified
        where_filter = None
        if document_id:
            where_filter = {"document_id": document_id}
        
        # Query collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter
        )
        
        # Format results with similarity scores
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            documents = results['documents'][0]
            distances = results['distances'][0]
            metadatas = results['metadatas'][0]
            
            for doc, distance, metadata in zip(documents, distances, metadatas):
                # Convert distance to similarity score (0-1, higher is better)
                # ChromaDB uses squared L2 distance, convert to cosine similarity approximation
                similarity_score = 1 / (1 + distance)
                formatted_results.append((doc, similarity_score, metadata))
        
        return formatted_results
    
    def delete_document(self, document_id: str) -> int:
        """
        Delete all chunks of a document from vector store.
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            Number of chunks deleted
        """
        # Get all chunk IDs for this document
        results = self.collection.get(
            where={"document_id": document_id}
        )
        
        if results['ids']:
            self.collection.delete(ids=results['ids'])
            return len(results['ids'])
        
        return 0
    
    def clear_collection(self):
        """Clear all documents from the collection."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Document embeddings for RAG"}
        )
    
    def get_collection_stats(self) -> dict:
        """Get statistics about the collection."""
        count = self.collection.count()
        return {
            "total_chunks": count,
            "collection_name": self.collection_name,
            "persist_directory": self.persist_directory
        }


# Global singleton instances
_persistent_store_instance: Optional[VectorStoreManager] = None
_temporary_store_instance: Optional[VectorStoreManager] = None


def get_vector_store(is_persistent: bool = True) -> VectorStoreManager:
    """
    Get or create vector store instance.
    
    Args:
        is_persistent: If True, returns the persistent store (disk-based).
                      If False, returns the temporary store (in-memory).
    """
    global _persistent_store_instance, _temporary_store_instance
    
    if is_persistent:
        if _persistent_store_instance is None:
            _persistent_store_instance = VectorStoreManager(is_persistent=True)
        return _persistent_store_instance
    else:
        if _temporary_store_instance is None:
            _temporary_store_instance = VectorStoreManager(
                collection_name="temp_documents", 
                is_persistent=False
            )
        return _temporary_store_instance
