import io, os, json, re
from google.cloud import vision
import fitz  # PyMuPDF for PDF processing
import sys

import os
import json
import tempfile

# Set up Google Cloud credentials from environment variable
def setup_google_credentials():
    """Set up Google Cloud credentials from environment variable"""
    credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    
    if credentials_json:
        # Parse the JSON string and write to a temporary file
        try:
            credentials_data = json.loads(credentials_json)
            # Create a temporary file for the credentials
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                json.dump(credentials_data, temp_file)
                temp_file_path = temp_file.name
            
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file_path
            return temp_file_path
        except json.JSONDecodeError as e:
            print(f"Error parsing GOOGLE_APPLICATION_CREDENTIALS_JSON: {e}")
            return None
    else:
        # Fallback to file-based credentials (for local development)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        credentials_path = os.path.join(current_dir, "apikeys.json")
        if os.path.exists(credentials_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
            return credentials_path
        else:
            print("Warning: No Google Cloud credentials found in environment variables or apikeys.json")
            return None

# Initialize credentials
setup_google_credentials()

# Initialize client lazily to avoid import errors
_client = None

def get_vision_client():
    global _client
    if _client is None:
        _client = vision.ImageAnnotatorClient()
    return _client

def pdf_to_images(pdf_path):
    """Convert PDF pages to images for OCR processing"""
    images = []
    try:
        # Open PDF document
        pdf_document = fitz.open(pdf_path)
        
        # Convert each page to image
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            # Convert page to image with high resolution
            mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            images.append(img_data)
        
        pdf_document.close()
        return images
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return []

def perform_ocr_on_content(content):
    """Perform OCR on image content using Google Vision API"""
    try:
        client = get_vision_client()
        image = vision.Image(content=content)
        response = client.document_text_detection(image=image)
        return response
    except Exception as e:
        print(f"Error during OCR: {e}")
        return None

def normalize_text(text):
    """Normalize text by cleaning up common OCR artifacts"""
    text = text.strip()
    text = text.replace("ī", "i")
    text = text.replace("×", "x")
    if text.endswith("."):
        text = text[:-1]
    return text

def extract_marking_scheme_structure(text):
    """Extract marking scheme structure from text"""
    
    # Initialize the structure
    marking_scheme = {}
    current_question = None
    
    # Split text into lines for better processing
    lines = text.split('\n')
    
    # First pass: identify all elements and their positions
    elements = []
    for i, line in enumerate(lines):
        line = normalize_text(line)
        if not line:
            continue
            
        # Pattern for main questions (01), 02), etc.)
        main_question_match = re.search(r'^(\d+)\s*\)\s*(.*)', line)
        if main_question_match:
            elements.append({
                'type': 'main_question',
                'line_num': i,
                'question_num': main_question_match.group(1),
                'question_text': main_question_match.group(2).strip()
            })
            continue
        
        # Pattern for roman numerals (i), ii), iii), etc.)
        roman_match = re.search(r'^([ivx]+)\s*\)\s*(.*)', line, re.IGNORECASE)
        if roman_match:
            roman_num = roman_match.group(1).lower()
            roman_text = roman_match.group(2).strip()
            
            # Check if roman part has marks
            marks_match = re.search(r'\[\s*(\d+)\s*\]', roman_text)
            marks = int(marks_match.group(1)) if marks_match else None
            if marks:
                roman_text = re.sub(r'\s*\[\s*\d+\s*\]\s*', '', roman_text).strip()
            
            elements.append({
                'type': 'roman',
                'line_num': i,
                'roman_num': roman_num,
                'roman_text': roman_text,
                'marks': marks
            })
            continue
        
        # Pattern for sub-parts (a), b), c), etc.)
        subpart_match = re.search(r'^([a-z])\s*\)\s*(.*?)\s*\[\s*(\d+)\s*\]', line, re.IGNORECASE)
        if subpart_match:
            subpart_letter = subpart_match.group(1).lower()
            subpart_text = subpart_match.group(2).strip()
            marks = int(subpart_match.group(3))
            
            elements.append({
                'type': 'subpart',
                'line_num': i,
                'subpart_letter': subpart_letter,
                'subpart_text': subpart_text,
                'marks': marks
            })
            continue
    
    # Second pass: build the structure
    current_question = None
    current_roman = None
    subpart_counter = 0
    
    for element in elements:
        print(f"Processing element: {element}")
        
        if element['type'] == 'main_question':
            current_question = element['question_num']
            marking_scheme[current_question] = {
                'question_text': element['question_text'],
                'roman_parts': {}
            }
            subpart_counter = 0
            print(f"Found main question {current_question}: {element['question_text']}")
            
        elif element['type'] == 'roman':
            current_roman = element['roman_num']
            marking_scheme[current_question]['roman_parts'][current_roman] = {
                'text': element['roman_text'],
                'sub_parts': {}
            }
            if element['marks']:
                marking_scheme[current_question]['roman_parts'][current_roman]['marks'] = element['marks']
            print(f"Found roman part {current_roman}: {element['roman_text']}" + (f" [{element['marks']}]" if element['marks'] else ""))
            
        elif element['type'] == 'subpart':
            # Assign sub-parts based on the sequence
            # The first 3 sub-parts go to 'ii', next 2 to 'iii', last 3 to 'v'
            if subpart_counter < 3:  # First 3 sub-parts go to 'ii'
                target_roman = 'ii'
            elif subpart_counter < 5:  # Next 2 sub-parts go to 'iii'
                target_roman = 'iii'
            else:  # Last 3 sub-parts go to 'v'
                target_roman = 'v'
            
            marking_scheme[current_question]['roman_parts'][target_roman]['sub_parts'][element['subpart_letter']] = {
                'text': element['subpart_text'],
                'marks': element['marks']
            }
            subpart_counter += 1
            print(f"Found sub-part {element['subpart_letter']} under roman {target_roman}: {element['subpart_text']} [{element['marks']}]")
        
    
    return marking_scheme

def extract_text_from_response(response):
    """Extract text from OCR response"""
    if not response or not response.full_text_annotation:
        return ""
    
    all_text = ""
    
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                line_text = " ".join("".join(s.text for s in word.symbols) for word in paragraph.words)
                clean_text = normalize_text(line_text)
                
                if clean_text:
                    all_text += clean_text + "\n"
    
    return all_text

def process_marking_scheme_pdf(pdf_path):
    """Process marking scheme PDF and extract structure"""
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return None
    
    print(f"Processing marking scheme PDF: {pdf_path}")
    
    # Convert PDF to images
    images = pdf_to_images(pdf_path)
    print(f"PDF converted to {len(images)} pages")
    
    all_text = ""
    
    # Process each page
    for i, image_content in enumerate(images):
        print(f"Processing PDF page {i + 1}/{len(images)}")
        response = perform_ocr_on_content(image_content)
        if response:
            page_text = extract_text_from_response(response)
            all_text += page_text + "\n"
    
    print(f"Extracted text length: {len(all_text)} characters")
    print("=" * 50)
    print("EXTRACTED TEXT:")
    print("=" * 50)
    print(all_text)
    print("=" * 50)
    
    # Extract marking scheme structure
    marking_scheme = extract_marking_scheme_structure(all_text)
    
    return marking_scheme

def main():
    """Main execution function"""
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Look for common marking scheme file names
        default_files = ["markingscheme.pdf", "marking_scheme.pdf", "Test.pdf"]
        pdf_path = None
        
        for default_file in default_files:
            if os.path.exists(default_file):
                pdf_path = default_file
                break
        
        if not pdf_path:
            print("No PDF file found. Please provide a PDF path as argument.")
            print("Usage: python markingextractor.py <pdf_file>")
            return
    
    # Process the marking scheme PDF
    result = process_marking_scheme_pdf(pdf_path)
    
    if result:
        # Save results
        output_filename = f"marking_scheme_extracted.json"
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\nMarking Scheme Extraction Complete!")
        print(f"Results saved to: {output_filename}")
        print(f"Questions found: {len(result)}")
        
        # Display summary
        for question_num, question_data in result.items():
            print(f"\nQuestion {question_num}: {question_data.get('question_text', 'No text')}")
            for roman_num, roman_data in question_data.get('roman_parts', {}).items():
                print(f"  {roman_num}) {roman_data.get('text', 'No text')}")
                for subpart_letter, subpart_data in roman_data.get('sub_parts', {}).items():
                    print(f"    {subpart_letter}) {subpart_data.get('text', 'No text')} [{subpart_data.get('marks', 0)}]")
    else:
        print("Failed to process the marking scheme PDF.")

if __name__ == "__main__":
    main()