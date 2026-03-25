"""
BERT Embedding Engine Module

This module handles the generation of BERT embeddings for text processing
using sentence-transformers library.
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Union
import streamlit as st


class EmbeddingEngine:
    """
    BERT-based embedding engine for text similarity analysis.
    
    Uses all-MiniLM-L6-v2 model for fast and accurate embeddings.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding engine with specified model.
        
        Args:
            model_name (str): Name of the sentence-transformer model
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    @st.cache_resource(show_spinner="Loading BERT model...")
    def _load_model():
        """
        Load the BERT model with caching for performance.
        """
        try:
            return SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            st.error(f"Failed to load BERT model: {e}")
            return None
    
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            self.model = self._load_model()
            if self.model is None:
                raise RuntimeError("Model loading returned None")
        except Exception as e:
            st.error(f"Error initializing embedding engine: {e}")
            self.model = None
    
    def generate_embedding(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Generate BERT embeddings for input text.
        
        Args:
            text (Union[str, List[str]]): Input text or list of texts
            
        Returns:
            np.ndarray: Embedding vector(s)
        """
        if self.model is None:
            # Fallback to simple embedding if model fails
            st.warning("BERT model not available, using fallback embedding")
            return self._fallback_embedding(text)
        
        if isinstance(text, str):
            text = [text]
        
        try:
            embeddings = self.model.encode(
                text,
                batch_size=32,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            return embeddings
        except Exception as e:
            st.error(f"Failed to generate embeddings: {e}")
            return self._fallback_embedding(text)
    
    def _fallback_embedding(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Fallback embedding method using simple text processing.
        
        Args:
            text (Union[str, List[str]]): Input text or list of texts
            
        Returns:
            np.ndarray: Simple embedding vector(s)
        """
        if isinstance(text, str):
            text = [text]
        
        # Simple character-based embedding as fallback
        embeddings = []
        for t in text:
            # Create a simple 384-dimensional embedding (same as MiniLM)
            embedding = np.zeros(384)
            if t:
                # Use character frequencies as simple features
                for i, char in enumerate(t[:384]):
                    embedding[i] = ord(char) / 255.0
            embeddings.append(embedding)
        
        return np.array(embeddings)
    
    def compute_cosine_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1 (np.ndarray): First embedding vector
            embedding2 (np.ndarray): Second embedding vector
            
        Returns:
            float: Cosine similarity score (0-1)
        """
        if embedding1.ndim == 1:
            embedding1 = embedding1.reshape(1, -1)
        if embedding2.ndim == 1:
            embedding2 = embedding2.reshape(1, -1)
        
        similarity = cosine_similarity(embedding1, embedding2)[0][0]
        return float(similarity)
    
    def normalize_score_to_percentage(self, similarity_score: float) -> float:
        """
        Normalize cosine similarity score to percentage (0-100).
        
        Args:
            similarity_score (float): Cosine similarity score (-1 to 1)
            
        Returns:
            float: Normalized percentage score (0-100)
        """
        # Convert from [-1, 1] to [0, 100]
        normalized = ((similarity_score + 1) / 2) * 100
        return round(normalized, 2)
    
    def batch_similarity(self, query_embedding: np.ndarray, 
                        candidate_embeddings: List[np.ndarray]) -> List[float]:
        """
        Compute similarity between query and multiple candidates.
        
        Args:
            query_embedding (np.ndarray): Query embedding vector
            candidate_embeddings (List[np.ndarray]): List of candidate embeddings
            
        Returns:
            List[float]: List of similarity scores
        """
        similarities = []
        for candidate_emb in candidate_embeddings:
            similarity = self.compute_cosine_similarity(query_embedding, candidate_emb)
            similarities.append(similarity)
        return similarities
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            int: Embedding dimension
        """
        if self.model is None:
            return 384  # Fallback dimension (same as MiniLM)
        
        try:
            # Generate a dummy embedding to get dimension
            dummy_embedding = self.generate_embedding("test")
            return dummy_embedding.shape[1]
        except Exception:
            return 384  # Fallback dimension
