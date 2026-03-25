"""
AI-Powered Resume Intelligence & Ranking System

A comprehensive recruitment automation tool that ranks resumes against job descriptions
using BERT embeddings, skill ontology mapping, bias detection, and explainable AI.
"""

from .embedding_engine import EmbeddingEngine
from .text_extractor import TextExtractor
from .skill_mapper import SkillMapper
from .bias_detector import BiasDetector
from .explainability_engine import ExplainabilityEngine
from .scoring_engine import ScoringEngine, CandidateResult
from .visualization import ResumeVisualizer

__version__ = "1.0.0"
__author__ = "AI Resume Ranking Team"

__all__ = [
    'EmbeddingEngine',
    'TextExtractor', 
    'SkillMapper',
    'BiasDetector',
    'ExplainabilityEngine',
    'ScoringEngine',
    'CandidateResult',
    'ResumeVisualizer'
]
