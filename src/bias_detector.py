"""
Bias Detection Module

This module detects potential bias in resumes and job descriptions
by identifying gender indicators, age indicators, and other
potentially biased content.
"""

import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class BiasType(Enum):
    """Types of bias that can be detected."""
    GENDER = "gender"
    AGE = "age"
    PERSONAL_ATTRIBUTES = "personal_attributes"
    UNNECESSARY_INFO = "unnecessary_info"


@dataclass
class BiasDetection:
    """Data class for bias detection results."""
    bias_type: BiasType
    detected_items: List[str]
    risk_level: str  # "low", "medium", "high"
    recommendations: List[str]


class BiasDetector:
    """
    Bias detection system for resumes and job descriptions.
    
    Detects presence of potentially biased content and provides recommendations.
    """
    
    def __init__(self):
        """Initialize the bias detector with patterns and dictionaries."""
        self._initialize_bias_patterns()
    
    def _initialize_bias_patterns(self):
        """Initialize bias detection patterns and dictionaries."""
        
        # Gender indicators
        self.gender_pronouns = {
            'male': ['he', 'him', 'his', 'himself'],
            'female': ['she', 'her', 'hers', 'herself']
        }
        
        self.gendered_words = {
            'male_biased': ['rockstar', 'ninja', 'guru', 'dominant', 'aggressive'],
            'female_biased': ['supportive', 'nurturing', 'collaborative', 'emotional']
        }
        
        # Age indicators
        self.age_indicators = [
            r'\b(\d{2})\s*years?\s*old\b',
            r'\bage\s*:\s*\d{2}\b',
            r'\bborn\s*in\s*\d{4}\b',
            r'\b(\d{2})\s*-\s*\d{2}\s*years?\s*(?:of\s*)?experience\b',
            r'\brecent\s*graduate\b',
            r'\byoung\s*professional\b',
            r'\bmature\s*professional\b',
            r'\bsenior\s*citizen\b'
        ]
        
        # Personal attributes that shouldn't influence hiring
        self.personal_attributes = [
            r'\bmarried\b',
            r'\bsingle\b',
            r'\bdivorced\b',
            r'\bchildren?\b',
            r'\bkids?\b',
            r'\bparent\b',
            r'\bmother\b',
            r'\bfather\b',
            r'\breligion\b',
            r'\breligious\b',
            r'\bnationality\b',
            r'\bethnicity\b',
            r'\brace\b',
            r'\bcolor\b',
            r'\bdisability\b',
            r'\bdisabled\b',
            r'\bhandicapped\b',
            r'\bhealth\s*condition\b'
        ]
        
        # Unnecessary personal information
        self.unnecessary_info = [
            r'\bheight\b',
            r'\bweight\b',
            r'\bphoto\b',
            r'\bportrait\b',
            r'\bhobbies\b',
            r'\binterests\b',
            r'\bactivities\b',
            r'\bsports\b',
            r'\bmusic\b',
            r'\btravel\b'
        ]
        
        # Job description bias patterns
        self.job_description_bias = {
            'gender_coded': [
                'dominant', 'competitive', 'aggressive', 'leader', 'ambitious',
                'assertive', 'decisive', 'outspoken', 'confident', 'independent'
            ],
            'age_discriminatory': [
                'young', 'energetic', 'dynamic', 'fresh', 'recent graduate',
                'digital native', 'mature', 'experienced professional', 'seasoned'
            ]
        }
    
    def analyze_text(self, text: str, text_type: str = "resume") -> Dict[str, Any]:
        """
        Analyze text for potential bias.
        
        Args:
            text (str): Text to analyze
            text_type (str): Type of text ("resume" or "job_description")
            
        Returns:
            Dict[str, Any]: Comprehensive bias analysis
        """
        text_lower = text.lower()
        
        bias_detections = []
        
        # Detect gender bias
        gender_bias = self._detect_gender_bias(text_lower, text_type)
        if gender_bias:
            bias_detections.append(gender_bias)
        
        # Detect age bias
        age_bias = self._detect_age_bias(text_lower, text_type)
        if age_bias:
            bias_detections.append(age_bias)
        
        # Detect personal attribute bias
        personal_bias = self._detect_personal_attributes(text_lower, text_type)
        if personal_bias:
            bias_detections.append(personal_bias)
        
        # Detect unnecessary information
        unnecessary_bias = self._detect_unnecessary_info(text_lower, text_type)
        if unnecessary_bias:
            bias_detections.append(unnecessary_bias)
        
        # Calculate overall risk score
        overall_risk = self._calculate_overall_risk(bias_detections)
        
        return {
            'overall_risk_score': overall_risk['score'],
            'overall_risk_level': overall_risk['level'],
            'bias_detections': bias_detections,
            'recommendations': self._generate_overall_recommendations(bias_detections, text_type),
            'text_type': text_type
        }
    
    def _detect_gender_bias(self, text: str, text_type: str) -> BiasDetection:
        """Detect gender-related bias in text."""
        detected_items = []
        
        # Check for gender pronouns
        for gender, pronouns in self.gender_pronouns.items():
            for pronoun in pronouns:
                if re.search(r'\b' + re.escape(pronoun) + r'\b', text):
                    detected_items.append(f"Gender pronoun: {pronoun}")
        
        # Check for gendered words
        for bias_type, words in self.gendered_words.items():
            for word in words:
                if re.search(r'\b' + re.escape(word) + r'\b', text):
                    detected_items.append(f"Gendered word: {word}")
        
        if not detected_items:
            return None
        
        risk_level = self._assess_risk_level(len(detected_items), BiasType.GENDER)
        recommendations = self._get_gender_bias_recommendations(detected_items, text_type)
        
        return BiasDetection(
            bias_type=BiasType.GENDER,
            detected_items=detected_items,
            risk_level=risk_level,
            recommendations=recommendations
        )
    
    def _detect_age_bias(self, text: str, text_type: str) -> BiasDetection:
        """Detect age-related bias in text."""
        detected_items = []
        
        for pattern in self.age_indicators:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                detected_items.append(f"Age indicator: {match}")
        
        if text_type == "job_description":
            for word in self.job_description_bias['age_discriminatory']:
                if re.search(r'\b' + re.escape(word) + r'\b', text):
                    detected_items.append(f"Age-coded word: {word}")
        
        if not detected_items:
            return None
        
        risk_level = self._assess_risk_level(len(detected_items), BiasType.AGE)
        recommendations = self._get_age_bias_recommendations(detected_items, text_type)
        
        return BiasDetection(
            bias_type=BiasType.AGE,
            detected_items=detected_items,
            risk_level=risk_level,
            recommendations=recommendations
        )
    
    def _detect_personal_attributes(self, text: str, text_type: str) -> BiasDetection:
        """Detect personal attributes that shouldn't influence hiring."""
        detected_items = []
        
        for pattern in self.personal_attributes:
            if re.search(pattern, text, re.IGNORECASE):
                detected_items.append(f"Personal attribute: {pattern}")
        
        if not detected_items:
            return None
        
        risk_level = self._assess_risk_level(len(detected_items), BiasType.PERSONAL_ATTRIBUTES)
        recommendations = self._get_personal_attribute_recommendations(detected_items, text_type)
        
        return BiasDetection(
            bias_type=BiasType.PERSONAL_ATTRIBUTES,
            detected_items=detected_items,
            risk_level=risk_level,
            recommendations=recommendations
        )
    
    def _detect_unnecessary_info(self, text: str, text_type: str) -> BiasDetection:
        """Detect unnecessary personal information."""
        detected_items = []
        
        for pattern in self.unnecessary_info:
            if re.search(pattern, text, re.IGNORECASE):
                detected_items.append(f"Unnecessary info: {pattern}")
        
        if not detected_items:
            return None
        
        risk_level = self._assess_risk_level(len(detected_items), BiasType.UNNECESSARY_INFO)
        recommendations = self._get_unnecessary_info_recommendations(detected_items, text_type)
        
        return BiasDetection(
            bias_type=BiasType.UNNECESSARY_INFO,
            detected_items=detected_items,
            risk_level=risk_level,
            recommendations=recommendations
        )
    
    def _assess_risk_level(self, detection_count: int, bias_type: BiasType) -> str:
        """Assess risk level based on detection count and bias type."""
        if detection_count == 0:
            return "low"
        elif detection_count <= 2:
            return "medium"
        else:
            return "high"
    
    def _get_gender_bias_recommendations(self, detected_items: List[str], text_type: str) -> List[str]:
        """Get recommendations for gender bias."""
        recommendations = []
        
        if text_type == "resume":
            recommendations.append("Consider removing gender pronouns from resume")
            recommendations.append("Focus on skills and qualifications rather than gendered language")
        else:
            recommendations.append("Use gender-neutral language in job description")
            recommendations.append("Consider using tools like Textio to reduce gender bias")
            recommendations.append("Avoid gender-coded words that may discourage certain applicants")
        
        return recommendations
    
    def _get_age_bias_recommendations(self, detected_items: List[str], text_type: str) -> List[str]:
        """Get recommendations for age bias."""
        recommendations = []
        
        if text_type == "resume":
            recommendations.append("Remove age indicators and date of birth")
            recommendations.append("Focus on recent and relevant experience")
        else:
            recommendations.append("Remove age-related requirements from job description")
            recommendations.append("Focus on skills and experience rather than age")
            recommendations.append("Use inclusive language like 'experienced' instead of age-specific terms")
        
        return recommendations
    
    def _get_personal_attribute_recommendations(self, detected_items: List[str], text_type: str) -> List[str]:
        """Get recommendations for personal attribute bias."""
        recommendations = []
        
        if text_type == "resume":
            recommendations.append("Remove personal information like marital status, family details")
            recommendations.append("Focus on professional qualifications only")
        else:
            recommendations.append("Ensure job requirements are job-related and business necessary")
            recommendations.append("Avoid questions about personal characteristics")
        
        return recommendations
    
    def _get_unnecessary_info_recommendations(self, detected_items: List[str], text_type: str) -> List[str]:
        """Get recommendations for unnecessary information."""
        recommendations = []
        
        if text_type == "resume":
            recommendations.append("Remove physical attributes like height, weight")
            recommendations.append("Remove personal hobbies unless relevant to job")
            recommendations.append("Avoid including photos unless required by local norms")
        
        return recommendations
    
    def _calculate_overall_risk(self, bias_detections: List[BiasDetection]) -> Dict[str, Any]:
        """Calculate overall risk score and level."""
        if not bias_detections:
            return {'score': 0, 'level': 'low'}
        
        # Weight different bias types
        risk_weights = {
            BiasType.GENDER: 0.3,
            BiasType.AGE: 0.3,
            BiasType.PERSONAL_ATTRIBUTES: 0.25,
            BiasType.UNNECESSARY_INFO: 0.15
        }
        
        total_score = 0
        total_weight = 0
        
        for detection in bias_detections:
            weight = risk_weights.get(detection.bias_type, 0.1)
            
            # Convert risk level to numeric score
            risk_scores = {'low': 1, 'medium': 2, 'high': 3}
            detection_score = risk_scores.get(detection.risk_level, 1)
            
            total_score += detection_score * weight
            total_weight += weight
        
        normalized_score = (total_score / total_weight) * 33.33  # Scale to 0-100
        
        if normalized_score <= 33:
            level = 'low'
        elif normalized_score <= 66:
            level = 'medium'
        else:
            level = 'high'
        
        return {
            'score': round(normalized_score, 2),
            'level': level
        }
    
    def _generate_overall_recommendations(self, bias_detections: List[BiasDetection], text_type: str) -> List[str]:
        """Generate overall recommendations based on all detected biases."""
        all_recommendations = []
        
        for detection in bias_detections:
            all_recommendations.extend(detection.recommendations)
        
        # Add general recommendations
        if text_type == "resume":
            all_recommendations.append("Review resume to ensure it focuses on professional qualifications")
            all_recommendations.append("Consider using blind resume format to reduce bias")
        else:
            all_recommendations.append("Consider using structured evaluation criteria")
            all_recommendations.append("Implement diverse hiring panel to reduce individual bias")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in all_recommendations:
            if rec not in seen:
                unique_recommendations.append(rec)
                seen.add(rec)
        
        return unique_recommendations
