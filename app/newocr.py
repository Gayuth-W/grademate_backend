import io, os, json, re
from google.cloud import vision
import fitz  # PyMuPDF for PDF processing
from PIL import Image
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

def get_file_extension(filename):
    """Get file extension from filename"""
    return os.path.splitext(filename)[1].lower()

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

def process_image_file(file_path):
    """Process image files (JPG, PNG) and return content"""
    try:
        with io.open(file_path, "rb") as image_file:
            content = image_file.read()
        return content
    except Exception as e:
        print(f"Error reading image file: {e}")
        return None

def process_pdf_file(file_path):
    """Process PDF file and return list of image contents"""
    try:
        images = pdf_to_images(file_path)
        return images
    except Exception as e:
        print(f"Error processing PDF file: {e}")
        return []

def perform_ocr_on_content(content):
    """Perform OCR on image content using Google Vision API"""
    try:
        client = get_vision_client()
        image = vision.Image(content=content)
        response = client.document_text_detection(image=image)
        
        # Check for errors in the response
        if response.error.message:
            print(f"Google Vision API error: {response.error.message}")
            return None
            
        return response
    except Exception as e:
        print(f"Error during OCR: {e}")
        return None

def is_metadata_line(text):
    """Check if a line contains metadata (student ID, subject ID, page number)"""
    metadata_patterns = [
        r'Student\s*No\s*:',
        r'Student\s*NO\s*:',
        r'Subject\s*No\s*:',
        r'Subject\s*NO\s*:',
        r'Page\s*No\s*:',
        r'Page\s*NO\s*:',
    ]
    
    for pattern in metadata_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def extract_metadata_from_text(text):
    """Extract student ID, subject ID, and page number using pattern matching"""
    student_id = None
    subject_id = None
    page_no = None
    
    print(f"Debug - Analyzing text: {text[:300]}...")
    
    # Student ID patterns - more flexible matching
    student_patterns = [
        r'Student\s*No\s*:\s*(\d+)',
        r'Student\s*NO\s*:\s*(\d+)',
        r'Student\s*Number\s*:\s*(\d+)',
        r'Student\s*ID\s*:\s*(\d+)',
        r'Student\s*No\s*:\s*(\w+)',
    ]
    
    for pattern in student_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            student_id = match.group(1).strip()
            print(f"Debug - Student ID pattern '{pattern}' matched: {student_id}")
            break
    
    # Subject ID patterns - improved to handle the specific format
    subject_patterns = [
        r'Subject\s*No\s*:\s*([A-Za-z0-9\s/\-]+?)(?:\s+Student|$)',
        r'Subject\s*NO\s*:\s*([A-Za-z0-9\s/\-]+?)(?:\s+Student|$)',
        r'Subject\s*Code\s*:\s*([A-Za-z0-9\s/\-]+?)(?:\s+Student|$)',
        r'Subject\s*ID\s*:\s*([A-Za-z0-9\s/\-]+?)(?:\s+Student|$)',
        r'Subject\s*No\s*:\s*([A-Za-z0-9\s/\-]+?)(?:\s+\d+\s*\)|$)',
    ]
    
    for pattern in subject_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            subject_id = match.group(1).strip()
            print(f"Debug - Subject ID pattern '{pattern}' matched: {subject_id}")
            break
    
    # Page number patterns
    page_patterns = [
        r'Page\s*No\s*:\s*(\d+)',
        r'Page\s*NO\s*:\s*(\d+)',
        r'Page\s*Number\s*:\s*(\d+)',
        r'Page\s*:\s*(\d+)',
    ]
    
    for pattern in page_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            page_no = match.group(1).strip()
            print(f"Debug - Page No pattern '{pattern}' matched: {page_no}")
            break
    
    return student_id, subject_id, page_no

def extract_text_from_response(response):
    """Extract and process text from OCR response"""
    if not response or not response.full_text_annotation:
        return None, None, None, []
    
    # First, collect all text to analyze for metadata
    all_text = ""
    answers_list = []
    
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                line_text = " ".join("".join(s.text for s in word.symbols) for word in paragraph.words)
                clean_text = normalize(line_text)
                
                if clean_text:
                    all_text += clean_text + " "
                    # Only add to answers if it's not a metadata line
                    if not is_metadata_line(line_text):
                        answers_list.append(line_text)
    
    # Extract metadata using pattern matching
    student_id, subject_id, page_no = extract_metadata_from_text(all_text)
    
    return student_id, subject_id, page_no, answers_list

def normalize(text: str) -> str:
    """Normalize text by cleaning up common OCR artifacts"""
    text = text.strip()
    text = text.replace("ī", "i")
    text = text.replace("×", "x")
    if text.endswith("."):
        text = text[:-1]
    return text

def process_file(file_path):
    """Main function to process any supported file format"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
    
    file_ext = get_file_extension(file_path)
    print(f"Processing file: {file_path} (Format: {file_ext})")
    
    all_answers = []
    final_student_id = None
    final_subject_id = None
    final_page_no = None
    
    if file_ext in ['.jpg', '.jpeg', '.png']:
        # Process image files
        content = process_image_file(file_path)
        if content:
            response = perform_ocr_on_content(content)
            if response:
                student_id, subject_id, page_no, answers = extract_text_from_response(response)
                if student_id:
                    final_student_id = student_id
                if subject_id:
                    final_subject_id = subject_id
                if page_no:
                    final_page_no = page_no
                all_answers.extend(answers)
    
    elif file_ext == '.pdf':
        # Process PDF files
        images = process_pdf_file(file_path)
        print(f"PDF converted to {len(images)} pages")
        
        for i, image_content in enumerate(images):
            print(f"Processing PDF page {i + 1}/{len(images)}")
            response = perform_ocr_on_content(image_content)
            if response:
                student_id, subject_id, page_no, answers = extract_text_from_response(response)
                # Use the first page's metadata, or update if found on later pages
                if not final_student_id and student_id:
                    final_student_id = student_id
                if not final_subject_id and subject_id:
                    final_subject_id = subject_id
                if not final_page_no and page_no:
                    final_page_no = page_no
                all_answers.extend(answers)
    
    else:
        print(f"Unsupported file format: {file_ext}")
        print("Supported formats: .jpg, .jpeg, .png, .pdf")
        return None
    
    # Combine all answers
    answers_text = " ".join(all_answers)
    
    result = {
        "student_id": final_student_id,
        "subject_id": final_subject_id,
        "page_no": final_page_no,
        "answers": answers_text,
        "file_processed": file_path,
        "file_format": file_ext
    }
    
    return result

def main():
    """Main execution function"""
    # Check if file path is provided as command line argument
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Default files to try in order
        default_files = ["Test.pdf", "Test16.jpg", "markingscheme.png"]
        file_path = None
        
        for default_file in default_files:
            if os.path.exists(default_file):
                file_path = default_file
                break
        
        if not file_path:
            print("No supported files found. Please provide a file path as argument.")
            print("Supported formats: .jpg, .jpeg, .png, .pdf")
            return
    
    # Process the file
    result = process_file(file_path)
    
    if result:
        # Save results
        output_filename = f"output_questions_{os.path.splitext(os.path.basename(file_path))[0]}.json"
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"Extraction Complete!")
        print(f"Results saved to: {output_filename}")
        print(f"Student ID: {result['student_id']}")
        print(f"Subject ID: {result['subject_id']}")
        print(f"Page No: {result['page_no']}")
        print(f"Answers extracted: {len(result['answers'])} characters")
    else:
        print("Failed to process the file.")

if __name__ == "__main__":
    main()