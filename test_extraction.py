#!/usr/bin/env python3
"""
Test script to debug text extraction issues
"""

import os
import sys
import json
from pathlib import Path

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_marking_extraction():
    """Test marking scheme extraction"""
    print("=" * 50)
    print("Testing Marking Scheme Extraction")
    print("=" * 50)
    
    try:
        import markingextractor
        
        # Test with existing PDF file
        test_files = [
            "app/marking.pdf",
            "app/Test.pdf",
            "app/marking_scheme_extracted.json"  # This should exist
        ]
        
        for file_path in test_files:
            if os.path.exists(file_path):
                print(f"\nFound test file: {file_path}")
                if file_path.endswith('.pdf'):
                    print(f"Testing PDF extraction: {file_path}")
                    result = markingextractor.process_marking_scheme_pdf(file_path)
                    if result:
                        print(f"✅ Successfully extracted {len(result)} questions")
                        print(f"Sample data: {json.dumps(list(result.keys())[:2], indent=2)}")
                    else:
                        print(f"❌ Failed to extract from {file_path}")
                elif file_path.endswith('.json'):
                    print(f"Found existing extracted data: {file_path}")
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        print(f"✅ Existing data has {len(data)} questions")
            else:
                print(f"❌ File not found: {file_path}")
                
    except Exception as e:
        print(f"❌ Error testing marking extraction: {e}")
        import traceback
        traceback.print_exc()

def test_answer_extraction():
    """Test answer sheet extraction"""
    print("\n" + "=" * 50)
    print("Testing Answer Sheet Extraction")
    print("=" * 50)
    
    try:
        import newocr
        
        # Test with existing files
        test_files = [
            "app/Test16.jpg",
            "app/Test.pdf",
            "app/output_questions_Test.json",  # This should exist
            "app/output_questions_Test16.json"  # This should exist
        ]
        
        for file_path in test_files:
            if os.path.exists(file_path):
                print(f"\nFound test file: {file_path}")
                if file_path.endswith(('.jpg', '.jpeg', '.png', '.pdf')):
                    print(f"Testing file extraction: {file_path}")
                    result = newocr.process_file(file_path)
                    if result:
                        print(f"✅ Successfully extracted data")
                        print(f"Student ID: {result.get('student_id', 'Not found')}")
                        print(f"Subject ID: {result.get('subject_id', 'Not found')}")
                        print(f"Answers length: {len(result.get('answers', ''))}")
                    else:
                        print(f"❌ Failed to extract from {file_path}")
                elif file_path.endswith('.json'):
                    print(f"Found existing extracted data: {file_path}")
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        print(f"✅ Existing data - Student: {data.get('student_id', 'Unknown')}")
            else:
                print(f"❌ File not found: {file_path}")
                
    except Exception as e:
        print(f"❌ Error testing answer extraction: {e}")
        import traceback
        traceback.print_exc()

def test_google_vision():
    """Test Google Vision API connection"""
    print("\n" + "=" * 50)
    print("Testing Google Vision API")
    print("=" * 50)
    
    try:
        from google.cloud import vision
        
        # Check if credentials are available (environment variable or file)
        creds_file = "app/apikeys.json"
        env_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        
        if env_creds:
            print("✅ Google Cloud credentials found in environment variable")
        elif os.path.exists(creds_file):
            print(f"✅ Credentials file found: {creds_file}")
        else:
            print("❌ No Google Cloud credentials found")
            return False
            
        # Try to create a client
        try:
            client = vision.ImageAnnotatorClient()
            print("✅ Google Vision client created successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to create Google Vision client: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Google Vision: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_methods():
    """Test fallback extraction methods"""
    print("\n" + "=" * 50)
    print("Testing Fallback Methods")
    print("=" * 50)
    
    try:
        import text_extraction_fallback
        
        # Test marking scheme fallback
        test_pdf = "app/marking.pdf"
        if os.path.exists(test_pdf):
            print(f"Testing marking scheme fallback with: {test_pdf}")
            result = text_extraction_fallback.extract_marking_scheme_fallback(test_pdf)
            if result:
                print(f"✅ Fallback extraction successful: {len(result)} questions")
                print(f"Sample questions: {list(result.keys())[:3]}")
            else:
                print(f"❌ Fallback extraction failed")
        else:
            print(f"❌ Test PDF not found: {test_pdf}")
            
        # Test answer sheet fallback
        test_image = "app/Test16.jpg"
        if os.path.exists(test_image):
            print(f"Testing answer sheet fallback with: {test_image}")
            result = text_extraction_fallback.extract_answer_sheet_fallback(test_image)
            if result:
                print(f"✅ Fallback extraction successful")
                print(f"Student ID: {result.get('student_id', 'Not found')}")
                print(f"Subject ID: {result.get('subject_id', 'Not found')}")
                print(f"Answers length: {len(result.get('answers', ''))}")
            else:
                print(f"❌ Fallback extraction failed")
        else:
            print(f"❌ Test image not found: {test_image}")
            
    except Exception as e:
        print(f"❌ Error testing fallback methods: {e}")
        import traceback
        traceback.print_exc()

def test_services():
    """Test the service layer"""
    print("\n" + "=" * 50)
    print("Testing Service Layer")
    print("=" * 50)
    
    try:
        from services import TextExtractionService
        
        # Test marking scheme extraction
        test_pdf = "app/marking.pdf"
        if os.path.exists(test_pdf):
            print(f"Testing marking scheme service with: {test_pdf}")
            success, data, error = TextExtractionService.extract_marking_scheme(test_pdf)
            if success:
                print(f"✅ Service extraction successful: {len(data)} questions")
            else:
                print(f"❌ Service extraction failed: {error}")
        else:
            print(f"❌ Test PDF not found: {test_pdf}")
            
        # Test answer sheet extraction
        test_image = "app/Test16.jpg"
        if os.path.exists(test_image):
            print(f"Testing answer sheet service with: {test_image}")
            success, data, error = TextExtractionService.extract_answer_sheet(test_image, True)
            if success:
                print(f"✅ Service extraction successful")
                print(f"Student ID: {data.get('student_id', 'Not found')}")
            else:
                print(f"❌ Service extraction failed: {error}")
        else:
            print(f"❌ Test image not found: {test_image}")
            
    except Exception as e:
        print(f"❌ Error testing services: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests"""
    print("GradeMate Text Extraction Debug Test")
    print("=" * 50)
    
    # Test Google Vision first
    vision_ok = test_google_vision()
    
    # Test fallback methods regardless of Google Vision status
    test_fallback_methods()
    
    if vision_ok:
        # Test individual extraction modules
        test_marking_extraction()
        test_answer_extraction()
        
        # Test service layer
        test_services()
    else:
        print("\n❌ Google Vision API not working. Using fallback methods.")
        print("Testing service layer with fallback methods...")
        test_services()
    
    print("\n" + "=" * 50)
    print("Debug test completed")
    print("=" * 50)

if __name__ == "__main__":
    main()
