"""
Scoring and Ranking Engine

This module handles the core scoring and ranking logic for resumes
against job descriptions using multiple weighted components.
"""

import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import streamlit as st
from sklearn.preprocessing import MinMaxScaler

from .embedding_engine import EmbeddingEngine
from .skill_mapper import SkillMapper
from .bias_detector import BiasDetector
from .explainability_engine import ExplainabilityEngine


@dataclass
class CandidateResult:
    """Data class for candidate analysis results."""
    filename: str
    name: str
    email: str
    phone: str
    text: str
    semantic_similarity: float
    skill_coverage: Dict[str, Any]
    years_of_experience: Optional[int]
    education: List[Dict[str, str]]
    bias_analysis: Dict[str, Any]
    final_score: float
    rank: int
    explanation: Optional[str] = None


class ScoringEngine:
    """
    Main scoring and ranking engine for resume analysis.
    
    Combines multiple scoring components to produce comprehensive rankings.
    """
    
    def __init__(self):
        """Initialize the scoring engine with all components."""
        self.embedding_engine = EmbeddingEngine()
        self.skill_mapper = SkillMapper()
        self.bias_detector = BiasDetector()
        self.explainability_engine = ExplainabilityEngine()
        
        # Scoring weights (configurable)
        self.weights = {
            'semantic_similarity': 0.6,
            'skill_match': 0.25,
            'experience_score': 0.1,
            'education_relevance': 0.05
        }
    
    def analyze_job_description(self, job_text: str) -> Dict[str, Any]:
        """
        Analyze job description to extract requirements.
        
        Args:
            job_text (str): Job description text
            
        Returns:
            Dict[str, Any]: Job analysis data
        """
        # Generate embedding for job description
        job_embedding = self.embedding_engine.generate_embedding(job_text)
        
        # Extract skills from job description
        job_skills = self.skill_mapper.extract_skills_from_text(job_text)
        
        # Detect bias in job description
        bias_analysis = self.bias_detector.analyze_text(job_text, "job_description")
        
        # Extract experience requirements
        experience_requirements = self._extract_experience_requirements(job_text)
        
        # Extract education requirements
        education_requirements = self._extract_education_requirements(job_text)
        
        return {
            'text': job_text,
            'embedding': job_embedding,
            'skills': job_skills,
            'bias_analysis': bias_analysis,
            'experience_requirements': experience_requirements,
            'education_requirements': education_requirements
        }
    
    def analyze_resume(self, resume_text: str, filename: str, 
                      job_analysis: Dict[str, Any]) -> CandidateResult:
        """
        Analyze a single resume against job requirements.
        
        Args:
            resume_text (str): Resume text content
            filename (str): Original filename
            job_analysis (Dict[str, Any]): Job analysis data
            
        Returns:
            CandidateResult: Complete analysis results
        """
        # Generate embedding for resume
        resume_embedding = self.embedding_engine.generate_embedding(resume_text)
        
        # Calculate semantic similarity
        semantic_similarity = self.embedding_engine.compute_cosine_similarity(
            resume_embedding, job_analysis['embedding']
        )
        semantic_similarity_pct = self.embedding_engine.normalize_score_to_percentage(
            semantic_similarity
        )
        
        # Extract skills from resume
        resume_skills = self.skill_mapper.extract_skills_from_text(resume_text)
        
        # Calculate skill coverage
        skill_coverage = self.skill_mapper.calculate_skill_coverage(
            job_analysis['skills'], resume_skills
        )
        
        # Extract contact information
        contact_info = self._extract_contact_info(resume_text)
        
        # Extract years of experience
        years_of_experience = self._extract_years_of_experience(resume_text)
        
        # Extract education information
        education = self._extract_education_info(resume_text)
        
        # Detect bias in resume
        bias_analysis = self.bias_detector.analyze_text(resume_text, "resume")
        
        # Calculate weighted final score
        final_score = self._calculate_final_score(
            semantic_similarity_pct,
            skill_coverage,
            years_of_experience,
            education,
            job_analysis
        )
        
        return CandidateResult(
            filename=filename,
            name=contact_info.get('name', 'Unknown'),
            email=contact_info.get('email', ''),
            phone=contact_info.get('phone', ''),
            text=resume_text,
            semantic_similarity=semantic_similarity_pct,
            skill_coverage=skill_coverage,
            years_of_experience=years_of_experience,
            education=education,
            bias_analysis=bias_analysis,
            final_score=final_score,
            rank=0  # Will be set during ranking
        )
    
    def rank_candidates(self, candidates: List[CandidateResult], 
                       job_analysis: Dict[str, Any]) -> List[CandidateResult]:
        """
        Rank candidates based on their scores and generate explanations.
        
        Args:
            candidates (List[CandidateResult]): List of candidate results
            job_analysis (Dict[str, Any]): Job analysis data
            
        Returns:
            List[CandidateResult]: Ranked candidates with explanations
        """
        # Sort candidates by final score (descending)
        candidates.sort(key=lambda x: x.final_score, reverse=True)
        
        # Assign ranks and generate explanations
        for rank, candidate in enumerate(candidates, 1):
            candidate.rank = rank
            
            # Generate explanation using explainability engine
            explanation = self.explainability_engine.generate_explanation(
                self._candidate_to_dict(candidate),
                job_analysis,
                rank
            )
            candidate.explanation = explanation.detailed_explanation
        
        return candidates
    
    def _calculate_final_score(self, semantic_similarity: float,
                             skill_coverage: Dict[str, Any],
                             years_of_experience: Optional[int],
                             education: List[Dict[str, str]],
                             job_analysis: Dict[str, Any]) -> float:
        """
        Calculate weighted final score for a candidate.
        
        Args:
            semantic_similarity (float): Semantic similarity percentage
            skill_coverage (Dict[str, Any]): Skill coverage analysis
            years_of_experience (Optional[int]): Years of experience
            education (List[Dict[str, str]]): Education information
            job_analysis (Dict[str, Any]): Job analysis data
            
        Returns:
            float: Final weighted score (0-100)
        """
        # Semantic similarity component
        semantic_score = semantic_similarity
        
        # Skill match component
        skill_score = skill_coverage.get('overall_coverage', 0)
        
        # Experience score component
        experience_score = self._calculate_experience_score(
            years_of_experience, job_analysis['experience_requirements']
        )
        
        # Education relevance component
        education_score = self._calculate_education_score(
            education, job_analysis['education_requirements']
        )
        
        # Calculate weighted final score
        final_score = (
            semantic_score * self.weights['semantic_similarity'] +
            skill_score * self.weights['skill_match'] +
            experience_score * self.weights['experience_score'] +
            education_score * self.weights['education_relevance']
        )
        
        return round(final_score, 2)
    
    def _calculate_experience_score(self, years_experience: Optional[int],
                                   experience_requirements: Dict[str, Any]) -> float:
        """Calculate experience alignment score."""
        if years_experience is None:
            return 50.0  # Neutral score if experience not detected
        
        required_years = experience_requirements.get('minimum_years', 0)
        preferred_years = experience_requirements.get('preferred_years', required_years + 2)
        
        if years_experience >= preferred_years:
            return 100.0
        elif years_experience >= required_years:
            ratio = (years_experience - required_years) / (preferred_years - required_years)
            return 50.0 + (ratio * 50.0) if preferred_years > required_years else 75.0
        elif years_experience > 0:
            return (years_experience / required_years) * 50.0 if required_years > 0 else 25.0
        else:
            return 0.0
    
    def _calculate_education_score(self, education: List[Dict[str, str]],
                                 education_requirements: Dict[str, Any]) -> float:
        """Calculate education relevance score."""
        if not education or not education_requirements:
            return 50.0  # Neutral score if data is missing
        
        required_level = education_requirements.get('minimum_level', '').lower()
        preferred_level = education_requirements.get('preferred_level', required_level).lower()
        
        education_levels = ['high school', 'bachelor', 'master', 'phd']
        
        candidate_level_score = 0
        for edu in education:
            level = edu.get('level', '').lower()
            if level in education_levels:
                candidate_level_score = max(candidate_level_score, education_levels.index(level))
        
        required_score = education_levels.index(required_level) if required_level in education_levels else 0
        preferred_score = education_levels.index(preferred_level) if preferred_level in education_levels else required_score
        
        if candidate_level_score >= preferred_score:
            return 100.0
        elif candidate_level_score >= required_score:
            return 75.0
        else:
            return 25.0
    
    def _extract_experience_requirements(self, job_text: str) -> Dict[str, Any]:
        """Extract experience requirements from job description."""
        import re
        
        # Pattern to match years of experience requirements
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'minimum\s*(?:of\s*)?(\d+)\s*years?',
            r'(\d+)\s*-\s*(\d+)\s*years?'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, job_text, re.IGNORECASE)
            if matches:
                if len(matches[0]) == 2:  # Range pattern
                    min_years, max_years = matches[0]
                    return {
                        'minimum_years': int(min_years),
                        'preferred_years': int(max_years)
                    }
                else:
                    years = int(matches[0][0] if isinstance(matches[0], tuple) else matches[0])
                    return {
                        'minimum_years': years,
                        'preferred_years': years + 2
                    }
        
        return {'minimum_years': 0, 'preferred_years': 0}
    
    def _extract_education_requirements(self, job_text: str) -> Dict[str, Any]:
        """Extract education requirements from job description."""
        import re
        
        education_keywords = {
            'phd': ['phd', 'doctorate', 'doctoral'],
            'master': ['master', 'm.s', 'msc', 'mba'],
            'bachelor': ['bachelor', 'b.s', 'bsc', 'undergraduate'],
            'high school': ['high school', 'ged']
        }
        
        job_text_lower = job_text.lower()
        
        for level, keywords in education_keywords.items():
            for keyword in keywords:
                if keyword in job_text_lower:
                    return {
                        'minimum_level': level,
                        'preferred_level': level
                    }
        
        return {'minimum_level': '', 'preferred_level': ''}
    
    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information from resume text."""
        from .text_extractor import TextExtractor
        extractor = TextExtractor()
        return extractor.extract_contact_info(text)
    
    def _extract_years_of_experience(self, text: str) -> Optional[int]:
        """Extract years of experience from resume text."""
        from .text_extractor import TextExtractor
        extractor = TextExtractor()
        return extractor.extract_years_of_experience(text)
    
    def _extract_education_info(self, text: str) -> List[Dict[str, str]]:
        """Extract education information from resume text."""
        import re
        
        education = []
        
        # Pattern to match education entries
        education_patterns = [
            r'(bachelor|master|phd|msc|bsc|mba|b\.s|m\.s|ph\.d)[^.]*',
            r'university[^.]*',
            r'college[^.]*'
        ]
        
        for pattern in education_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                education.append({
                    'level': match,
                    'institution': '',
                    'year': ''
                })
        
        return education
    
    def _candidate_to_dict(self, candidate: CandidateResult) -> Dict[str, Any]:
        """Convert CandidateResult to dictionary for explainability engine."""
        return {
            'name': candidate.name,
            'semantic_similarity': candidate.semantic_similarity,
            'skill_coverage': candidate.skill_coverage,
            'years_of_experience': candidate.years_of_experience,
            'education': candidate.education,
            'final_score': candidate.final_score,
            'rank': candidate.rank
        }
    
    def update_weights(self, new_weights: Dict[str, float]):
        """
        Update scoring weights.
        
        Args:
            new_weights (Dict[str, float]): New weight values
        """
        # Validate weights sum to 1.0
        total_weight = sum(new_weights.values())
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total_weight}")
        
        self.weights.update(new_weights)
    
    def get_current_weights(self) -> Dict[str, float]:
        """Get current scoring weights."""
        return self.weights.copy()
    
    def compare_candidates(self, candidate1: CandidateResult, 
                          candidate2: CandidateResult) -> Dict[str, Any]:
        """
        Compare two candidates side by side.
        
        Args:
            candidate1 (CandidateResult): First candidate
            candidate2 (CandidateResult): Second candidate
            
        Returns:
            Dict[str, Any]: Comparison results
        """
        comparison = {
            'candidate1': {
                'name': candidate1.name,
                'score': candidate1.final_score,
                'semantic_similarity': candidate1.semantic_similarity,
                'skill_coverage': candidate1.skill_coverage.get('overall_coverage', 0),
                'years_experience': candidate1.years_of_experience or 0
            },
            'candidate2': {
                'name': candidate2.name,
                'score': candidate2.final_score,
                'semantic_similarity': candidate2.semantic_similarity,
                'skill_coverage': candidate2.skill_coverage.get('overall_coverage', 0),
                'years_experience': candidate2.years_of_experience or 0
            },
            'differences': {},
            'winner': candidate1.name if candidate1.final_score > candidate2.final_score else candidate2.name
        }
        
        # Calculate differences
        for metric in ['score', 'semantic_similarity', 'skill_coverage', 'years_experience']:
            val1 = comparison['candidate1'][metric]
            val2 = comparison['candidate2'][metric]
            comparison['differences'][metric] = val1 - val2
        
        return comparison
