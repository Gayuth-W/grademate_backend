#!/usr/bin/env python3
"""
Debug script to test grading functionality
"""

import os
import sys
import json

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_parse_misc():
    """Test the parse_misc function with real data"""
    print("Testing parse_misc function")
    print("=" * 50)
    
    try:
        from Grading import parse_misc
        
        # Test with existing answer data
        answer_file = "app/output_questions_Test.json"
        if os.path.exists(answer_file):
            with open(answer_file, 'r') as f:
                data = json.load(f)
                answers_text = data.get('answers', '')
                print(f"Original answers text: {answers_text[:200]}...")
                print(f"Full answers text: {answers_text}")
                
                # Parse the answers
                parsed = parse_misc(answers_text)
                print(f"\nParsed answers: {json.dumps(parsed, indent=2)}")
                
                return parsed
        else:
            print(f"Answer file not found: {answer_file}")
            return None
            
    except Exception as e:
        print(f"Error testing parse_misc: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_marking_scheme():
    """Test marking scheme structure"""
    print("\nTesting marking scheme structure")
    print("=" * 50)
    
    try:
        marking_file = "app/marking_scheme_extracted.json"
        if os.path.exists(marking_file):
            with open(marking_file, 'r') as f:
                ms = json.load(f)
                print(f"Marking scheme structure: {json.dumps(ms, indent=2)}")
                return ms
        else:
            print(f"Marking scheme file not found: {marking_file}")
            return None
            
    except Exception as e:
        print(f"Error testing marking scheme: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_grade_question():
    """Test individual question grading"""
    print("\nTesting individual question grading")
    print("=" * 50)
    
    try:
        from Grading import grade_question
        
        # Test with a simple example
        student_answer = "3.5 billion years ago"
        rubric_text = "about 3.5 billion"
        max_mark = 1
        
        print(f"Student answer: {student_answer}")
        print(f"Rubric text: {rubric_text}")
        print(f"Max mark: {max_mark}")
        
        result = grade_question("1i", student_answer, rubric_text, max_mark)
        print(f"Grading result: {json.dumps(result, indent=2)}")
        
        return result
        
    except Exception as e:
        print(f"Error testing grade_question: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_full_grading():
    """Test full grading process"""
    print("\nTesting full grading process")
    print("=" * 50)
    
    try:
        from Grading import grade_student
        
        # Get parsed answers
        std_answers = test_parse_misc()
        if not std_answers:
            print("No parsed answers available")
            return
        
        # Get marking scheme
        ms = test_marking_scheme()
        if not ms:
            print("No marking scheme available")
            return
        
        print(f"\nStudent answers: {json.dumps(std_answers, indent=2)}")
        print(f"Marking scheme keys: {list(ms.keys())}")
        
        # Test grading
        result = grade_student("3992101102", std_answers, ms)
        print(f"\nGrading result: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"Error testing full grading: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests"""
    print("GradeMate Grading Debug Test")
    print("=" * 50)
    
    test_parse_misc()
    test_marking_scheme()
    test_grade_question()
    test_full_grading()
    
    print("\n" + "=" * 50)
    print("Debug test completed")
    print("=" * 50)

if __name__ == "__main__":
    main()
