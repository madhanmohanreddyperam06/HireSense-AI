"""
Skill Ontology Mapping Module

This module handles skill extraction and mapping using the predefined
skill ontology for categorizing and matching skills.
"""

import json
import re
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict
import streamlit as st


class SkillMapper:
    """
    Skill ontology mapper for extracting and categorizing skills from text.
    """
    
    def __init__(self, ontology_path: str = "data/skill_ontology.json"):
        """
        Initialize the skill mapper with ontology.
        
        Args:
            ontology_path (str): Path to the skill ontology JSON file
        """
        self.ontology_path = ontology_path
        self.ontology = None
        self.skill_cache = {}
        self._load_ontology()
    
    @st.cache_resource(show_spinner="Loading skill ontology...")
    def _load_ontology():
        """
        Load skill ontology with caching.
        """
        try:
            with open("data/skill_ontology.json", 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Failed to load skill ontology: {e}")
            return {}
    
    def _load_ontology(self):
        """Load the skill ontology from JSON file."""
        try:
            self.ontology = self._load_ontology()
            if not self.ontology:
                st.error("Skill ontology could not be loaded")
                self.ontology = {}
        except Exception as e:
            st.error(f"Error loading skill ontology: {e}")
            self.ontology = {}
    
    def extract_skills_from_text(self, text: str) -> Dict[str, List[str]]:
        """
        Extract skills from text using the ontology.
        
        Args:
            text (str): Input text (resume or job description)
            
        Returns:
            Dict[str, List[str]]: Categorized skills found in text
        """
        if not self.ontology:
            st.warning("No skill ontology available")
            return {}
        
        text_lower = text.lower()
        found_skills = defaultdict(list)
        
        for category, data in self.ontology.items():
            # Check explicit skills
            for skill in data['skills']:
                if self._find_skill_in_text(skill, text_lower):
                    found_skills[category].append(skill)
            
            # Check keywords for broader matching
            for keyword in data['keywords']:
                if keyword.lower() in text_lower:
                    # If keyword found, try to extract specific skills
                    related_skills = self._extract_related_skills(keyword, text_lower, data['skills'])
                    found_skills[category].extend(related_skills)
        
        # Remove duplicates while preserving order
        for category in found_skills:
            found_skills[category] = list(dict.fromkeys(found_skills[category]))
        
        return dict(found_skills)
    
    def _find_skill_in_text(self, skill: str, text: str) -> bool:
        """
        Check if a skill is present in text using word boundaries.
        
        Args:
            skill (str): Skill to search for
            text (str): Text to search in
            
        Returns:
            bool: True if skill is found
        """
        # Create word boundary pattern for exact matching
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        return bool(re.search(pattern, text))
    
    def _extract_related_skills(self, keyword: str, text: str, skill_list: List[str]) -> List[str]:
        """
        Extract skills related to a keyword from text.
        
        Args:
            keyword (str): Keyword found in text
            text (str): Text to search in
            skill_list (List[str]): List of skills to check against
            
        Returns:
            List[str]: Related skills found
        """
        related_skills = []
        keyword_context = self._get_keyword_context(keyword, text)
        
        for skill in skill_list:
            if skill.lower() in keyword_context:
                related_skills.append(skill)
        
        return related_skills
    
    def _get_keyword_context(self, keyword: str, text: str, window: int = 50) -> str:
        """
        Get context around a keyword in text.
        
        Args:
            keyword (str): Keyword to find context for
            text (str): Full text
            window (int): Number of characters before and after keyword
            
        Returns:
            str: Context around the keyword
        """
        positions = [m.start() for m in re.finditer(re.escape(keyword), text, re.IGNORECASE)]
        
        if not positions:
            return ""
        
        contexts = []
        for pos in positions:
            start = max(0, pos - window)
            end = min(len(text), pos + len(keyword) + window)
            contexts.append(text[start:end])
        
        return " ".join(contexts)
    
    def calculate_skill_coverage(self, job_skills: Dict[str, List[str]], 
                               resume_skills: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Calculate skill coverage percentage between job and resume.
        
        Args:
            job_skills (Dict[str, List[str]]): Skills required for job
            resume_skills (Dict[str, List[str]]): Skills found in resume
            
        Returns:
            Dict[str, Any]: Skill coverage analysis
        """
        coverage_analysis = {
            'overall_coverage': 0,
            'category_coverage': {},
            'matched_skills': [],
            'missing_skills': [],
            'extra_skills': []
        }
        
        total_job_skills = 0
        total_matched_skills = 0
        
        for category, job_skill_list in job_skills.items():
            resume_skill_list = resume_skills.get(category, [])
            
            # Calculate matches for this category
            matched = set(job_skill_list) & set(resume_skill_list)
            missing = set(job_skill_list) - set(resume_skill_list)
            
            category_coverage = len(matched) / len(job_skill_list) * 100 if job_skill_list else 0
            
            coverage_analysis['category_coverage'][category] = {
                'coverage_percentage': round(category_coverage, 2),
                'matched_skills': list(matched),
                'missing_skills': list(missing),
                'total_required': len(job_skill_list),
                'total_matched': len(matched)
            }
            
            total_job_skills += len(job_skill_list)
            total_matched_skills += len(matched)
            
            coverage_analysis['matched_skills'].extend(list(matched))
            coverage_analysis['missing_skills'].extend(list(missing))
        
        # Calculate overall coverage
        coverage_analysis['overall_coverage'] = round(
            (total_matched_skills / total_job_skills * 100) if total_job_skills > 0 else 0, 2
        )
        
        # Find extra skills in resume
        all_job_skills = set()
        for skill_list in job_skills.values():
            all_job_skills.update(skill_list)
        
        all_resume_skills = set()
        for skill_list in resume_skills.values():
            all_resume_skills.update(skill_list)
        
        coverage_analysis['extra_skills'] = list(all_resume_skills - all_job_skills)
        
        return coverage_analysis
    
    def get_skill_importance_weights(self) -> Dict[str, float]:
        """
        Get importance weights for different skill categories.
        
        Returns:
            Dict[str, float]: Weight mapping for categories
        """
        # Default weights - can be made configurable
        return {
            'Programming': 0.25,
            'Machine Learning': 0.20,
            'Web Development': 0.15,
            'Databases': 0.10,
            'Cloud & DevOps': 0.10,
            'Data Engineering': 0.10,
            'Mobile Development': 0.05,
            'Cybersecurity': 0.03,
            'Project Management': 0.01,
            'Soft Skills': 0.01
        }
    
    def calculate_weighted_skill_score(self, job_skills: Dict[str, List[str]], 
                                     resume_skills: Dict[str, List[str]]) -> float:
        """
        Calculate weighted skill match score.
        
        Args:
            job_skills (Dict[str, List[str]]): Job required skills
            resume_skills (Dict[str, List[str]]): Resume skills
            
        Returns:
            float: Weighted skill score (0-100)
        """
        weights = self.get_skill_importance_weights()
        total_weight = 0
        weighted_score = 0
        
        for category, job_skill_list in job_skills.items():
            if not job_skill_list:
                continue
            
            resume_skill_list = resume_skills.get(category, [])
            matched = set(job_skill_list) & set(resume_skill_list)
            
            category_score = len(matched) / len(job_skill_list)
            category_weight = weights.get(category, 0.01)
            
            weighted_score += category_score * category_weight
            total_weight += category_weight
        
        # Normalize to 0-100 scale
        final_score = (weighted_score / total_weight * 100) if total_weight > 0 else 0
        return round(final_score, 2)
    
    def get_skill_radar_data(self, job_skills: Dict[str, List[str]], 
                           resume_skills: Dict[str, List[str]]) -> Dict[str, List]:
        """
        Prepare data for radar chart visualization.
        
        Args:
            job_skills (Dict[str, List[str]]): Job required skills
            resume_skills (Dict[str, List[str]]): Resume skills
            
        Returns:
            Dict[str, List]: Data formatted for radar chart
        """
        categories = []
        job_coverage = []
        resume_coverage = []
        
        all_categories = set(job_skills.keys()) | set(resume_skills.keys())
        
        for category in sorted(all_categories):
            categories.append(category)
            
            job_skill_list = job_skills.get(category, [])
            resume_skill_list = resume_skills.get(category, [])
            
            # Calculate coverage percentages
            if job_skill_list:
                matched = set(job_skill_list) & set(resume_skill_list)
                job_coverage.append(100)  # Job represents 100% requirement
                resume_coverage.append(len(matched) / len(job_skill_list) * 100)
            else:
                job_coverage.append(0)
                resume_coverage.append(0)
        
        return {
            'categories': categories,
            'job_requirements': job_coverage,
            'resume_match': resume_coverage
        }
