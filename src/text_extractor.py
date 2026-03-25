"""
Text Extraction Module

This module handles text extraction from PDF and DOCX files
using pdfplumber and python-docx libraries.
"""

import pdfplumber
import docx
from typing import Optional, Dict, Any
import re
import streamlit as st
from io import BytesIO


class TextExtractor:
    """
    Text extraction utility for PDF and DOCX files.
    """
    
    def __init__(self):
        """Initialize the text extractor."""
        self.supported_formats = ['.pdf', '.docx']
    
    def extract_text_from_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Extract text from uploaded file.
        
        Args:
            file_content (bytes): File content in bytes
            filename (str): Name of the uploaded file
            
        Returns:
            Dict[str, Any]: Extracted text and metadata
        """
        file_extension = self._get_file_extension(filename)
        
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        try:
            if file_extension == '.pdf':
                return self._extract_from_pdf(file_content, filename)
            elif file_extension == '.docx':
                return self._extract_from_docx(file_content, filename)
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from {filename}: {e}")
    
    def _extract_from_pdf(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Extract text from PDF file.
        
        Args:
            file_content (bytes): PDF file content
            filename (str): Name of the file
            
        Returns:
            Dict[str, Any]: Extracted text and metadata
        """
        text_content = []
        metadata = {
            'filename': filename,
            'file_type': 'PDF',
            'num_pages': 0,
            'extraction_method': 'pdfplumber'
        }
        
        try:
            with pdfplumber.open(BytesIO(file_content)) as pdf:
                metadata['num_pages'] = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
            
            full_text = '\n'.join(text_content)
            
            return {
                'text': full_text,
                'metadata': metadata,
                'pages_text': text_content,
                'success': True
            }
            
        except Exception as e:
            return {
                'text': '',
                'metadata': metadata,
                'pages_text': [],
                'success': False,
                'error': str(e)
            }
    
    def _extract_from_docx(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Extract text from DOCX file.
        
        Args:
            file_content (bytes): DOCX file content
            filename (str): Name of the file
            
        Returns:
            Dict[str, Any]: Extracted text and metadata
        """
        text_content = []
        metadata = {
            'filename': filename,
            'file_type': 'DOCX',
            'num_paragraphs': 0,
            'extraction_method': 'python-docx'
        }
        
        try:
            doc = docx.Document(BytesIO(file_content))
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content.append(paragraph.text)
            
            metadata['num_paragraphs'] = len(text_content)
            full_text = '\n'.join(text_content)
            
            return {
                'text': full_text,
                'metadata': metadata,
                'pages_text': text_content,
                'success': True
            }
            
        except Exception as e:
            return {
                'text': '',
                'metadata': metadata,
                'pages_text': [],
                'success': False,
                'error': str(e)
            }
    
    def _get_file_extension(self, filename: str) -> str:
        """
        Get file extension from filename.
        
        Args:
            filename (str): Name of the file
            
        Returns:
            str: File extension (including dot)
        """
        return filename.lower().split('.')[-1] if '.' in filename else ''
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text (str): Raw extracted text
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere with processing
        text = re.sub(r'[^\w\s\-\.,;:!?()[]{}"\'@#$%&*+=<>|/\\]', '', text)
        
        # Normalize line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()
    
    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """
        Extract contact information from text.
        
        Args:
            text (str): Resume text
            
        Returns:
            Dict[str, str]: Extracted contact information
        """
        contact_info = {}
        
        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Phone extraction (basic patterns)
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 123-456-7890
            r'\b\(\d{3}\)\s?\d{3}[-.]?\d{4}\b',  # (123) 456-7890
            r'\b\d{10}\b'  # 1234567890
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                contact_info['phone'] = phones[0]
                break
        
        # LinkedIn extraction
        linkedin_pattern = r'linkedin\.com/in/[A-Za-z0-9-]+'
        linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_matches:
            contact_info['linkedin'] = 'https://' + linkedin_matches[0]
        
        return contact_info
    
    def extract_years_of_experience(self, text: str) -> Optional[int]:
        """
        Extract years of experience from text.
        
        Args:
            text (str): Resume text
            
        Returns:
            Optional[int]: Total years of experience
        """
        # Pattern to match "X years experience" or similar
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'experience:\s*(\d+)\+?\s*years?',
            r'(\d+)\+?\s*years?\s*(?:of\s*)?work',
            r'total\s*experience:\s*(\d+)\+?\s*years?'
        ]
        
        years = []
        for pattern in experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            years.extend([int(match) for match in matches])
        
        if years:
            # Return the maximum years found (likely total experience)
            return max(years)
        
        return None
