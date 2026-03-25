"""
Explainable AI Layer

This module provides explainability for the ranking system,
generating detailed explanations for why candidates are ranked
the way they are.
"""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import re


@dataclass
class ScoreComponent:
    """Data class for individual score components."""
    name: str
    value: float
    weight: float
    contribution: float
    description: str


@dataclass
class RankingExplanation:
    """Data class for ranking explanation."""
    candidate_name: str
    rank: int
    final_score: float
    score_components: List[ScoreComponent]
    key_strengths: List[str]
    areas_for_improvement: List[str]
    detailed_explanation: str


class ExplainabilityEngine:
    """
    Explainable AI engine for resume ranking system.
    
    Provides detailed explanations for ranking decisions.
    """
    
    def __init__(self):
        """Initialize the explainability engine."""
        self.score_weights = {
            'semantic_similarity': 0.6,
            'skill_match': 0.25,
            'experience_score': 0.1,
            'education_relevance': 0.05
        }
    
    def generate_explanation(self, candidate_data: Dict[str, Any], 
                           job_data: Dict[str, Any],
                           rank: int) -> RankingExplanation:
        """
        Generate comprehensive explanation for candidate ranking.
        
        Args:
            candidate_data (Dict[str, Any]): Candidate analysis data
            job_data (Dict[str, Any]): Job description data
            rank (int): Candidate's rank position
            
        Returns:
            RankingExplanation: Detailed explanation object
        """
        # Extract score components
        score_components = self._extract_score_components(candidate_data, job_data)
        
        # Calculate final score
        final_score = sum(comp.contribution for comp in score_components)
        
        # Generate key strengths and areas for improvement
        key_strengths = self._identify_key_strengths(candidate_data, job_data)
        areas_for_improvement = self._identify_improvement_areas(candidate_data, job_data)
        
        # Generate detailed explanation
        detailed_explanation = self._generate_detailed_explanation(
            candidate_data, job_data, score_components, key_strengths, areas_for_improvement
        )
        
        return RankingExplanation(
            candidate_name=candidate_data.get('name', 'Unknown Candidate'),
            rank=rank,
            final_score=round(final_score, 2),
            score_components=score_components,
            key_strengths=key_strengths,
            areas_for_improvement=areas_for_improvement,
            detailed_explanation=detailed_explanation
        )
    
    def _extract_score_components(self, candidate_data: Dict[str, Any], 
                                job_data: Dict[str, Any]) -> List[ScoreComponent]:
        """Extract and calculate individual score components."""
        components = []
        
        # Semantic similarity component
        semantic_score = candidate_data.get('semantic_similarity', 0)
        semantic_weight = self.score_weights['semantic_similarity']
        semantic_contribution = semantic_score * semantic_weight
        
        components.append(ScoreComponent(
            name='Semantic Similarity',
            value=semantic_score,
            weight=semantic_weight,
            contribution=semantic_contribution,
            description=f'Matches job description content and context ({semantic_score:.1f}%)'
        ))
        
        # Skill match component
        skill_coverage = candidate_data.get('skill_coverage', {}).get('overall_coverage', 0)
        skill_weight = self.score_weights['skill_match']
        skill_contribution = skill_coverage * skill_weight
        
        components.append(ScoreComponent(
            name='Skill Match',
            value=skill_coverage,
            weight=skill_weight,
            contribution=skill_contribution,
            description=f'Overall skill coverage ({skill_coverage:.1f}%)'
        ))
        
        # Experience score component
        experience_score = self._calculate_experience_score(candidate_data, job_data)
        experience_weight = self.score_weights['experience_score']
        experience_contribution = experience_score * experience_weight
        
        components.append(ScoreComponent(
            name='Experience Alignment',
            value=experience_score,
            weight=experience_weight,
            contribution=experience_contribution,
            description=f'Relevant experience alignment ({experience_score:.1f}%)'
        ))
        
        # Education relevance component
        education_score = self._calculate_education_score(candidate_data, job_data)
        education_weight = self.score_weights['education_relevance']
        education_contribution = education_score * education_weight
        
        components.append(ScoreComponent(
            name='Education Relevance',
            value=education_score,
            weight=education_weight,
            contribution=education_contribution,
            description=f'Education alignment ({education_score:.1f}%)'
        ))
        
        return components
    
    def _calculate_experience_score(self, candidate_data: Dict[str, Any], 
                                 job_data: Dict[str, Any]) -> float:
        """Calculate experience alignment score."""
        candidate_experience = candidate_data.get('years_of_experience', 0)
        job_requirements = job_data.get('experience_requirements', {})
        
        required_years = job_requirements.get('minimum_years', 0)
        preferred_years = job_requirements.get('preferred_years', required_years + 2)
        
        if candidate_experience >= preferred_years:
            return 100.0
        elif candidate_experience >= required_years:
            # Linear scaling between required and preferred
            ratio = (candidate_experience - required_years) / (preferred_years - required_years)
            return 50.0 + (ratio * 50.0)
        elif candidate_experience > 0:
            # Partial credit for some experience
            return (candidate_experience / required_years) * 50.0 if required_years > 0 else 0
        else:
            return 0.0
    
    def _calculate_education_score(self, candidate_data: Dict[str, Any], 
                                 job_data: Dict[str, Any]) -> float:
        """Calculate education relevance score."""
        candidate_education = candidate_data.get('education', [])
        job_education = job_data.get('education_requirements', {})
        
        if not candidate_education or not job_education:
            return 50.0  # Neutral score if data is missing
        
        required_level = job_education.get('minimum_level', '')
        preferred_level = job_education.get('preferred_level', required_level)
        
        education_levels = ['high_school', 'bachelor', 'master', 'phd']
        
        candidate_level_score = 0
        for education in candidate_education:
            level = education.get('level', '').lower()
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
    
    def _identify_key_strengths(self, candidate_data: Dict[str, Any], 
                               job_data: Dict[str, Any]) -> List[str]:
        """Identify candidate's key strengths relative to job requirements."""
        strengths = []
        
        # Semantic similarity strength
        semantic_score = candidate_data.get('semantic_similarity', 0)
        if semantic_score >= 80:
            strengths.append(f"Excellent semantic match with job description ({semantic_score:.0f}%)")
        elif semantic_score >= 65:
            strengths.append(f"Strong semantic match with job description ({semantic_score:.0f}%)")
        
        # Skill strengths
        skill_coverage = candidate_data.get('skill_coverage', {})
        category_coverage = skill_coverage.get('category_coverage', {})
        
        for category, coverage_data in category_coverage.items():
            coverage_pct = coverage_data.get('coverage_percentage', 0)
            if coverage_pct >= 80:
                matched_count = coverage_data.get('total_matched', 0)
                total_count = coverage_data.get('total_required', 0)
                strengths.append(f"Strong {category} skills ({matched_count}/{total_count} matched)")
        
        # Experience strength
        experience_years = candidate_data.get('years_of_experience', 0)
        if experience_years >= 5:
            strengths.append(f"Substantial professional experience ({experience_years} years)")
        
        # Education strength
        education = candidate_data.get('education', [])
        for edu in education:
            level = edu.get('level', '').lower()
            if 'master' in level or 'phd' in level:
                strengths.append(f"Advanced education ({edu.get('level', '')})")
                break
        
        return strengths[:5]  # Limit to top 5 strengths
    
    def _identify_improvement_areas(self, candidate_data: Dict[str, Any], 
                                  job_data: Dict[str, Any]) -> List[str]:
        """Identify areas where candidate could improve."""
        improvements = []
        
        # Skill gaps
        skill_coverage = candidate_data.get('skill_coverage', {})
        missing_skills = skill_coverage.get('missing_skills', [])
        
        if missing_skills:
            improvements.append(f"Missing key skills: {', '.join(missing_skills[:5])}")
        
        # Category gaps
        category_coverage = skill_coverage.get('category_coverage', {})
        for category, coverage_data in category_coverage.items():
            coverage_pct = coverage_data.get('coverage_percentage', 0)
            if coverage_pct < 50:
                missing_count = coverage_data.get('total_required', 0) - coverage_data.get('total_matched', 0)
                improvements.append(f"Improve {category} skills ({missing_count} missing)")
        
        # Experience gap
        experience_years = candidate_data.get('years_of_experience', 0)
        job_requirements = job_data.get('experience_requirements', {})
        required_years = job_requirements.get('minimum_years', 0)
        
        if experience_years < required_years:
            gap = required_years - experience_years
            improvements.append(f"Gain {gap} more years of relevant experience")
        
        # Education gap
        education = candidate_data.get('education', [])
        job_education = job_data.get('education_requirements', {})
        required_level = job_education.get('minimum_level', '')
        
        if required_level and not any(required_level.lower() in edu.get('level', '').lower() for edu in education):
            improvements.append(f"Consider {required_level} degree or equivalent certification")
        
        return improvements[:5]  # Limit to top 5 improvement areas
    
    def _generate_detailed_explanation(self, candidate_data: Dict[str, Any], 
                                     job_data: Dict[str, Any],
                                     score_components: List[ScoreComponent],
                                     key_strengths: List[str],
                                     areas_for_improvement: List[str]) -> str:
        """Generate detailed narrative explanation."""
        candidate_name = candidate_data.get('name', 'Candidate')
        final_score = sum(comp.contribution for comp in score_components)
        
        explanation = f"Candidate ranked #{candidate_data.get('rank', 1)} with a score of {final_score:.1f}/100.\n\n"
        
        # Score breakdown
        explanation += "**Score Breakdown:**\n"
        for component in score_components:
            explanation += f"- {component.name}: {component.value:.1f}% (weight: {component.weight*100:.0f}%, contribution: {component.contribution:.1f}%)\n"
        
        explanation += "\n**Key Strengths:**\n"
        for strength in key_strengths:
            explanation += f"- {strength}\n"
        
        if areas_for_improvement:
            explanation += "\n**Areas for Improvement:**\n"
            for improvement in areas_for_improvement:
                explanation += f"- {improvement}\n"
        
        # Overall assessment
        explanation += "\n**Overall Assessment:**\n"
        if final_score >= 80:
            explanation += f"{candidate_name} is an excellent match for this position with strong alignment across all key dimensions."
        elif final_score >= 65:
            explanation += f"{candidate_name} is a good match with solid qualifications, though there are some areas for development."
        elif final_score >= 50:
            explanation += f"{candidate_name} shows potential but has significant gaps in key requirements."
        else:
            explanation += f"{candidate_name} has limited alignment with the position requirements."
        
        return explanation
    
    def generate_comparison_explanation(self, candidate1_data: Dict[str, Any], 
                                      candidate2_data: Dict[str, Any]) -> str:
        """Generate explanation comparing two candidates."""
        name1 = candidate1_data.get('name', 'Candidate 1')
        name2 = candidate2_data.get('name', 'Candidate 2')
        score1 = candidate1_data.get('final_score', 0)
        score2 = candidate2_data.get('final_score', 0)
        
        explanation = f"**Comparison: {name1} vs {name2}**\n\n"
        explanation += f"Scores: {name1} ({score1:.1f}) vs {name2} ({score2:.1f})\n\n"
        
        # Compare key components
        components = ['semantic_similarity', 'skill_coverage', 'years_of_experience']
        
        for component in components:
            if component in candidate1_data and component in candidate2_data:
                val1 = candidate1_data[component]
                val2 = candidate2_data[component]
                
                if isinstance(val1, dict) and 'overall_coverage' in val1:
                    val1 = val1['overall_coverage']
                if isinstance(val2, dict) and 'overall_coverage' in val2:
                    val2 = val2['overall_coverage']
                
                diff = val1 - val2
                if abs(diff) > 5:  # Only show significant differences
                    leader = name1 if diff > 0 else name2
                    explanation += f"- {component.replace('_', ' ').title()}: {leader} leads by {abs(diff):.1f} points\n"
        
        return explanation
    
    def get_score_breakdown_data(self, explanation: RankingExplanation) -> Dict[str, List]:
        """Get data for score breakdown visualization."""
        return {
            'components': [comp.name for comp in explanation.score_components],
            'values': [comp.value for comp in explanation.score_components],
            'contributions': [comp.contribution for comp in explanation.score_components],
            'weights': [comp.weight * 100 for comp in explanation.score_components]
        }
