"""
Fallback text extraction methods that don't require Google Vision API
"""

import os
import json
import re
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from typing import Dict, Any, Optional, Tuple

def extract_text_from_pdf_fallback(pdf_path: str) -> str:
    """Extract text from PDF using PyMuPDF (fallback method)"""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_image_fallback(image_path: str) -> str:
    """Extract text from image using Tesseract OCR (fallback method)"""
    try:
        # Try to use Tesseract if available
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        # Return a placeholder text to prevent complete failure
        return f"[Image file: {os.path.basename(image_path)} - OCR not available]"

def extract_marking_scheme_fallback(pdf_path: str) -> Optional[Dict[str, Any]]:
    """Extract marking scheme structure using fallback method"""
    try:
        text = extract_text_from_pdf_fallback(pdf_path)
        if not text:
            return None
        
        # Simple pattern matching for marking scheme
        marking_scheme = {}
        lines = text.split('\n')
        
        current_question = None
        current_roman = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Pattern for main questions (01), 02), etc.)
            main_question_match = re.search(r'^(\d+)\s*\)\s*(.*)', line)
            if main_question_match:
                current_question = main_question_match.group(1)
                marking_scheme[current_question] = {
                    'question_text': main_question_match.group(2).strip(),
                    'roman_parts': {}
                }
                continue
            
            # Pattern for roman numerals (i), ii), iii), etc.)
            roman_match = re.search(r'^([ivx]+)\s*\)\s*(.*)', line, re.IGNORECASE)
            if roman_match and current_question:
                current_roman = roman_match.group(1).lower()
                roman_text = roman_match.group(2).strip()
                
                # Check for marks
                marks_match = re.search(r'\[\s*(\d+)\s*\]', roman_text)
                marks = int(marks_match.group(1)) if marks_match else 1
                if marks_match:
                    roman_text = re.sub(r'\s*\[\s*\d+\s*\]\s*', '', roman_text).strip()
                
                marking_scheme[current_question]['roman_parts'][current_roman] = {
                    'text': roman_text,
                    'marks': marks,
                    'sub_parts': {}
                }
                continue
            
            # Pattern for sub-parts (a), b), c), etc.)
            subpart_match = re.search(r'^([a-z])\s*\)\s*(.*?)\s*\[\s*(\d+)\s*\]', line, re.IGNORECASE)
            if subpart_match and current_question and current_roman:
                subpart_letter = subpart_match.group(1).lower()
                subpart_text = subpart_match.group(2).strip()
                marks = int(subpart_match.group(3))
                
                marking_scheme[current_question]['roman_parts'][current_roman]['sub_parts'][subpart_letter] = {
                    'text': subpart_text,
                    'marks': marks
                }
        
        return marking_scheme if marking_scheme else None
        
    except Exception as e:
        print(f"Error in fallback marking scheme extraction: {e}")
        return None

def extract_answer_sheet_fallback(file_path: str) -> Optional[Dict[str, Any]]:
    """Extract answers from answer sheet using fallback method"""
    try:
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            text = extract_text_from_pdf_fallback(file_path)
        elif file_ext in ['.jpg', '.jpeg', '.png']:
            text = extract_text_from_image_fallback(file_path)
        else:
            return None
        
        if not text:
            return None
        
        # Extract metadata
        student_id = None
        subject_id = None
        page_no = None
        
        # Student ID patterns
        student_patterns = [
            r'Student\s*No\s*:\s*(\d+)',
            r'Student\s*NO\s*:\s*(\d+)',
            r'Student\s*Number\s*:\s*(\d+)',
            r'Student\s*ID\s*:\s*(\d+)',
        ]
        
        for pattern in student_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                student_id = match.group(1).strip()
                break
        
        # Subject ID patterns
        subject_patterns = [
            r'Subject\s*No\s*:\s*([A-Za-z0-9\s/\-]+?)(?:\s+Student|$)',
            r'Subject\s*NO\s*:\s*([A-Za-z0-9\s/\-]+?)(?:\s+Student|$)',
        ]
        
        for pattern in subject_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                subject_id = match.group(1).strip()
                break
        
        # Page number patterns
        page_patterns = [
            r'Page\s*No\s*:\s*(\d+)',
            r'Page\s*NO\s*:\s*(\d+)',
        ]
        
        for pattern in page_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                page_no = match.group(1).strip()
                break
        
        return {
            "student_id": student_id,
            "subject_id": subject_id,
            "page_no": page_no,
            "answers": text,
            "file_processed": file_path,
            "file_format": file_ext[1:]  # Remove the dot
        }
        
    except Exception as e:
        print(f"Error in fallback answer sheet extraction: {e}")
        return None
