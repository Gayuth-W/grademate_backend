#!/usr/bin/env python3
"""
Simple test for text extraction without relative imports
"""

import os
import sys
import json

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_marking_scheme_fallback():
    """Test marking scheme extraction with fallback"""
    print("Testing Marking Scheme Fallback Extraction")
    print("=" * 50)
    
    try:
        import text_extraction_fallback
        
        test_files = [
            "app/marking.pdf",
            "app/Test.pdf"
        ]
        
        for file_path in test_files:
            if os.path.exists(file_path):
                print(f"\nTesting: {file_path}")
                result = text_extraction_fallback.extract_marking_scheme_fallback(file_path)
                if result:
                    print(f"✅ Successfully extracted {len(result)} questions")
                    for q_num, q_data in list(result.items())[:2]:  # Show first 2 questions
                        print(f"  Question {q_num}: {q_data.get('question_text', 'No text')[:50]}...")
                        for roman, roman_data in q_data.get('roman_parts', {}).items():
                            print(f"    {roman}) {roman_data.get('text', 'No text')[:30]}... [{roman_data.get('marks', 0)} marks]")
                else:
                    print(f"❌ Failed to extract from {file_path}")
            else:
                print(f"❌ File not found: {file_path}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_answer_sheet_fallback():
    """Test answer sheet extraction with fallback"""
    print("\nTesting Answer Sheet Fallback Extraction")
    print("=" * 50)
    
    try:
        import text_extraction_fallback
        
        test_files = [
            "app/Test16.jpg",
            "app/Test.pdf"
        ]
        
        for file_path in test_files:
            if os.path.exists(file_path):
                print(f"\nTesting: {file_path}")
                result = text_extraction_fallback.extract_answer_sheet_fallback(file_path)
                if result:
                    print(f"✅ Successfully extracted data")
                    print(f"  Student ID: {result.get('student_id', 'Not found')}")
                    print(f"  Subject ID: {result.get('subject_id', 'Not found')}")
                    print(f"  Page No: {result.get('page_no', 'Not found')}")
                    print(f"  Answers length: {len(result.get('answers', ''))} characters")
                    print(f"  File format: {result.get('file_format', 'Unknown')}")
                else:
                    print(f"❌ Failed to extract from {file_path}")
            else:
                print(f"❌ File not found: {file_path}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_existing_data():
    """Test with existing extracted data"""
    print("\nTesting Existing Extracted Data")
    print("=" * 50)
    
    # Check for existing marking scheme data
    marking_file = "app/marking_scheme_extracted.json"
    if os.path.exists(marking_file):
        print(f"Found existing marking scheme: {marking_file}")
        with open(marking_file, 'r') as f:
            data = json.load(f)
            print(f"✅ Contains {len(data)} questions")
            for q_num in list(data.keys())[:2]:
                print(f"  Question {q_num}: {data[q_num].get('question_text', 'No text')[:50]}...")
    
    # Check for existing answer sheet data
    answer_files = [
        "app/output_questions_Test.json",
        "app/output_questions_Test16.json"
    ]
    
    for answer_file in answer_files:
        if os.path.exists(answer_file):
            print(f"\nFound existing answer sheet: {answer_file}")
            with open(answer_file, 'r') as f:
                data = json.load(f)
                print(f"✅ Student ID: {data.get('student_id', 'Not found')}")
                print(f"✅ Subject ID: {data.get('subject_id', 'Not found')}")
                print(f"✅ Answers length: {len(data.get('answers', ''))} characters")

def main():
    """Run all tests"""
    print("GradeMate Simple Text Extraction Test")
    print("=" * 50)
    
    test_marking_scheme_fallback()
    test_answer_sheet_fallback()
    test_existing_data()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()
