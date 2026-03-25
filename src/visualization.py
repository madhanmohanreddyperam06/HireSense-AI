"""
Visualization Module

This module creates various visualizations for the resume ranking system
using Plotly for interactive charts and graphs.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import streamlit as st


class ResumeVisualizer:
    """
    Visualization class for resume ranking system.
    
    Creates interactive charts for ranking analysis, skill coverage,
    bias analysis, and candidate comparisons.
    """
    
    def __init__(self):
        """Initialize the visualizer with default color scheme."""
        self.color_scheme = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#ff7f0e',
            'danger': '#d62728',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40'
        }
    
    def create_ranking_bar_chart(self, candidates: List[Dict[str, Any]]) -> go.Figure:
        """
        Create a horizontal bar chart showing candidate rankings.
        
        Args:
            candidates (List[Dict[str, Any]]): List of ranked candidates
            
        Returns:
            go.Figure: Plotly bar chart
        """
        # Prepare data
        names = [c.get('name', f"Candidate {i+1}") for i, c in enumerate(candidates)]
        scores = [c.get('final_score', 0) for c in candidates]
        
        # Create color gradient based on scores
        colors = [self._get_score_color(score) for score in scores]
        
        # Create figure
        fig = go.Figure(data=[
            go.Bar(
                y=names,
                x=scores,
                orientation='h',
                marker_color=colors,
                text=[f"{score:.1f}" for score in scores],
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>'
            )
        ])
        
        # Update layout
        fig.update_layout(
            title="Candidate Rankings",
            xaxis_title="Final Score",
            yaxis_title="Candidates",
            height=max(400, len(candidates) * 40),
            margin=dict(l=150, r=50, t=50, b=50),
            showlegend=False
        )
        
        # Reverse y-axis to show highest score at top
        fig.update_yaxes(autorange="reversed")
        
        return fig
    
    def create_skill_radar_chart(self, job_skills: Dict[str, List[str]], 
                                resume_skills: Dict[str, List[str]]) -> go.Figure:
        """
        Create a radar chart comparing job requirements with resume skills.
        
        Args:
            job_skills (Dict[str, List[str]]): Job required skills
            resume_skills (Dict[str, List[str]]): Resume skills
            
        Returns:
            go.Figure: Plotly radar chart
        """
        # Get all categories
        all_categories = set(job_skills.keys()) | set(resume_skills.keys())
        categories = sorted(list(all_categories))
        
        # Calculate coverage percentages
        job_values = []
        resume_values = []
        
        for category in categories:
            job_skill_list = job_skills.get(category, [])
            resume_skill_list = resume_skills.get(category, [])
            
            if job_skill_list:
                matched = set(job_skill_list) & set(resume_skill_list)
                job_values.append(100)  # Job represents 100% requirement
                resume_values.append(len(matched) / len(job_skill_list) * 100)
            else:
                job_values.append(0)
                resume_values.append(0)
        
        # Create radar chart
        fig = go.Figure()
        
        # Add job requirements trace
        fig.add_trace(go.Scatterpolar(
            r=job_values,
            theta=categories,
            fill='toself',
            name='Job Requirements',
            line_color=self.color_scheme['primary'],
            fillcolor=f"rgba(31, 119, 180, 0.25)"
        ))
        
        # Add resume skills trace
        fig.add_trace(go.Scatterpolar(
            r=resume_values,
            theta=categories,
            fill='toself',
            name='Resume Match',
            line_color=self.color_scheme['success'],
            fillcolor=f"rgba(44, 160, 44, 0.25)"
        ))
        
        # Update layout
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    tickfont=dict(size=10)
                )
            ),
            title="Skill Coverage Analysis",
            height=500,
            showlegend=True
        )
        
        return fig
    
    def create_score_breakdown_chart(self, score_components: Dict[str, List]) -> go.Figure:
        """
        Create a stacked bar chart showing score breakdown.
        
        Args:
            score_components (Dict[str, List]): Score component data
            
        Returns:
            go.Figure: Plotly stacked bar chart
        """
        components = score_components['components']
        values = score_components['values']
        contributions = score_components['contributions']
        
        # Create figure
        fig = go.Figure(data=[
            go.Bar(
                x=components,
                y=contributions,
                marker_color=[self._get_component_color(comp) for comp in components],
                text=[f"{val:.1f}%" for val in values],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Value: %{customdata:.1f}%<br>Contribution: %{y:.1f}<extra></extra>',
                customdata=values
            )
        ])
        
        # Update layout
        fig.update_layout(
            title="Score Breakdown",
            xaxis_title="Score Components",
            yaxis_title="Contribution to Final Score",
            height=400,
            showlegend=False
        )
        
        return fig
    
    def create_bias_risk_gauge(self, bias_score: float) -> go.Figure:
        """
        Create a gauge chart for bias risk assessment.
        
        Args:
            bias_score (float): Bias risk score (0-100)
            
        Returns:
            go.Figure: Plotly gauge chart
        """
        # Determine risk level and color
        if bias_score <= 33:
            risk_level = "Low Risk"
            color = self.color_scheme['success']
        elif bias_score <= 66:
            risk_level = "Medium Risk"
            color = self.color_scheme['warning']
        else:
            risk_level = "High Risk"
            color = self.color_scheme['danger']
        
        # Create gauge chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = bias_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"Bias Risk Score - {risk_level}"},
            delta = {'reference': 50},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 33], 'color': "lightgreen"},
                    {'range': [33, 66], 'color': "yellow"},
                    {'range': [66, 100], 'color': "lightcoral"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))
        
        fig.update_layout(height=400)
        
        return fig
    
    def create_similarity_heatmap(self, candidates: List[Dict[str, Any]], 
                                 job_embedding: np.ndarray) -> go.Figure:
        """
        Create a heatmap showing similarity between candidates and job.
        
        Args:
            candidates (List[Dict[str, Any]]): List of candidates
            job_embedding (np.ndarray): Job description embedding
            
        Returns:
            go.Figure: Plotly heatmap
        """
        # Prepare data
        names = [c.get('name', f"Candidate {i+1}") for i, c in enumerate(candidates)]
        similarities = [c.get('semantic_similarity', 0) for c in candidates]
        
        # Create heatmap data
        heatmap_data = [similarities]
        
        # Create figure
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=names,
            y=['Job Description'],
            colorscale='RdYlBu_r',
            text=[[f"{score:.1f}%" for score in similarities]],
            texttemplate="%{text}",
            textfont={"size": 12},
            hovertemplate='Candidate: %{x}<br>Similarity: %{z:.1f}%<extra></extra>'
        ))
        
        # Update layout
        fig.update_layout(
            title="Semantic Similarity Heatmap",
            xaxis_title="Candidates",
            yaxis_title="Job Description",
            height=200,
            margin=dict(l=50, r=50, t=50, b=150)
        )
        
        # Rotate x-axis labels for better readability
        fig.update_xaxes(tickangle=45)
        
        return fig
    
    def create_candidate_comparison_chart(self, candidate1: Dict[str, Any], 
                                        candidate2: Dict[str, Any]) -> go.Figure:
        """
        Create a comparison chart for two candidates.
        
        Args:
            candidate1 (Dict[str, Any]): First candidate data
            candidate2 (Dict[str, Any]): Second candidate data
            
        Returns:
            go.Figure: Plotly comparison chart
        """
        # Metrics to compare
        metrics = ['Final Score', 'Semantic Similarity', 'Skill Coverage', 'Experience Score']
        
        # Extract values
        values1 = [
            candidate1.get('final_score', 0),
            candidate1.get('semantic_similarity', 0),
            candidate1.get('skill_coverage', {}).get('overall_coverage', 0),
            candidate1.get('years_experience', 0) * 10  # Scale experience for visibility
        ]
        
        values2 = [
            candidate2.get('final_score', 0),
            candidate2.get('semantic_similarity', 0),
            candidate2.get('skill_coverage', {}).get('overall_coverage', 0),
            candidate2.get('years_experience', 0) * 10  # Scale experience for visibility
        ]
        
        # Create figure
        fig = go.Figure()
        
        # Add candidate 1
        fig.add_trace(go.Bar(
            name=candidate1.get('name', 'Candidate 1'),
            x=metrics,
            y=values1,
            marker_color=self.color_scheme['primary']
        ))
        
        # Add candidate 2
        fig.add_trace(go.Bar(
            name=candidate2.get('name', 'Candidate 2'),
            x=metrics,
            y=values2,
            marker_color=self.color_scheme['secondary']
        ))
        
        # Update layout
        fig.update_layout(
            title="Candidate Comparison",
            xaxis_title="Metrics",
            yaxis_title="Score",
            height=400,
            barmode='group',
            showlegend=True
        )
        
        # Rotate x-axis labels
        fig.update_xaxes(tickangle=45)
        
        return fig
    
    def create_skill_category_chart(self, skill_coverage: Dict[str, Any]) -> go.Figure:
        """
        Create a bar chart showing skill coverage by category.
        
        Args:
            skill_coverage (Dict[str, Any]): Skill coverage analysis
            
        Returns:
            go.Figure: Plotly bar chart
        """
        category_coverage = skill_coverage.get('category_coverage', {})
        
        if not category_coverage:
            # Return empty chart if no data
            fig = go.Figure()
            fig.update_layout(title="No Skill Coverage Data Available")
            return fig
        
        categories = list(category_coverage.keys())
        coverage_percentages = [data.get('coverage_percentage', 0) for data in category_coverage.values()]
        matched_counts = [data.get('total_matched', 0) for data in category_coverage.values()]
        total_counts = [data.get('total_required', 0) for data in category_coverage.values()]
        
        # Create figure
        fig = go.Figure(data=[
            go.Bar(
                x=categories,
                y=coverage_percentages,
                marker_color=[self._get_coverage_color(pct) for pct in coverage_percentages],
                text=[f"{pct:.1f}% ({matched}/{total})" for pct, matched, total in 
                      zip(coverage_percentages, matched_counts, total_counts)],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Coverage: %{y:.1f}%<br>Matched: %{customdata[0]}/{customdata[1]}<extra></extra>',
                customdata=list(zip(matched_counts, total_counts))
            )
        ])
        
        # Update layout
        fig.update_layout(
            title="Skill Coverage by Category",
            xaxis_title="Skill Categories",
            yaxis_title="Coverage Percentage",
            height=400,
            showlegend=False
        )
        
        # Rotate x-axis labels
        fig.update_xaxes(tickangle=45)
        
        return fig
    
    def create_experience_distribution_chart(self, candidates: List[Dict[str, Any]]) -> go.Figure:
        """
        Create a histogram showing experience distribution.
        
        Args:
            candidates (List[Dict[str, Any]]): List of candidates
            
        Returns:
            go.Figure: Plotly histogram
        """
        # Extract experience years
        experience_years = [c.get('years_of_experience', 0) for c in candidates if c.get('years_of_experience') is not None]
        
        if not experience_years:
            # Return empty chart if no data
            fig = go.Figure()
            fig.update_layout(title="No Experience Data Available")
            return fig
        
        # Create histogram
        fig = go.Figure(data=[
            go.Histogram(
                x=experience_years,
                nbinsx=10,
                marker_color=self.color_scheme['info'],
                opacity=0.75,
                hovertemplate='Experience: %{x} years<br>Count: %{y}<extra></extra>'
            )
        ])
        
        # Update layout
        fig.update_layout(
            title="Experience Distribution",
            xaxis_title="Years of Experience",
            yaxis_title="Number of Candidates",
            height=400,
            showlegend=False
        )
        
        return fig
    
    def _get_score_color(self, score: float) -> str:
        """Get color based on score value."""
        if score >= 80:
            return self.color_scheme['success']
        elif score >= 65:
            return self.color_scheme['info']
        elif score >= 50:
            return self.color_scheme['warning']
        else:
            return self.color_scheme['danger']
    
    def _get_component_color(self, component: str) -> str:
        """Get color for score component."""
        component_colors = {
            'Semantic Similarity': self.color_scheme['primary'],
            'Skill Match': self.color_scheme['success'],
            'Experience Alignment': self.color_scheme['info'],
            'Education Relevance': self.color_scheme['warning']
        }
        return component_colors.get(component, self.color_scheme['secondary'])
    
    def _get_coverage_color(self, coverage: float) -> str:
        """Get color based on coverage percentage."""
        if coverage >= 80:
            return self.color_scheme['success']
        elif coverage >= 60:
            return self.color_scheme['info']
        elif coverage >= 40:
            return self.color_scheme['warning']
        else:
            return self.color_scheme['danger']
    
    def export_chart_as_html(self, fig: go.Figure, filename: str) -> str:
        """
        Export chart as HTML string.
        
        Args:
            fig (go.Figure): Plotly figure
            filename (str): Filename for the chart
            
        Returns:
            str: HTML string
        """
        return fig.to_html(include_plotlyjs='cdn', div_id=filename.replace(' ', '_'))
    
    def create_dashboard_summary(self, candidates: List[Dict[str, Any]], 
                               job_analysis: Dict[str, Any]) -> Dict[str, go.Figure]:
        """
        Create a complete dashboard with all key visualizations.
        
        Args:
            candidates (List[Dict[str, Any]]): List of ranked candidates
            job_analysis (Dict[str, Any]): Job analysis data
            
        Returns:
            Dict[str, go.Figure]: Dictionary of all charts
        """
        charts = {}
        
        # Ranking chart
        charts['ranking'] = self.create_ranking_bar_chart(candidates)
        
        # Skill radar chart (for top candidate)
        if candidates:
            top_candidate = candidates[0]
            charts['skill_radar'] = self.create_skill_radar_chart(
                job_analysis['skills'],
                top_candidate.get('skill_coverage', {}).get('matched_skills', {})
            )
        
        # Experience distribution
        charts['experience_dist'] = self.create_experience_distribution_chart(candidates)
        
        # Similarity heatmap
        if job_analysis.get('embedding') is not None:
            charts['similarity_heatmap'] = self.create_similarity_heatmap(
                candidates, job_analysis['embedding']
            )
        
        return charts
