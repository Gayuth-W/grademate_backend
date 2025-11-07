#!/usr/bin/env python3
"""
Final test for grading functionality
"""

import os
import sys
import json

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_grading_with_debug():
    """Test grading with detailed debug output"""
    print("Testing Grading with Debug Output")
    print("=" * 50)
    
    try:
        from Grading import grade_student, parse_misc
        
        # Get parsed answers
        answer_file = "app/output_questions_Test.json"
        with open(answer_file, 'r') as f:
            data = json.load(f)
            answers_text = data.get('answers', '')
        
        std_answers = parse_misc(answers_text)
        print(f"Student answers: {json.dumps(std_answers, indent=2)}")
        
        # Get marking scheme
        marking_file = "app/marking_scheme_extracted.json"
        with open(marking_file, 'r') as f:
            ms = json.load(f)
        
        print(f"\nMarking scheme keys: {list(ms.keys())}")
        
        # Test grading with debug
        print(f"\nStarting grading process...")
        
        # Manually trace through the grading process
        total_score = 0
        total_max = 0
        feedback_log = []
        recom_log = []
        
        for q, q_data in ms.items():
            print(f"\nProcessing question {q}")
            
            # Try to match question numbers
            std_q = std_answers.get(q, {})
            if not std_q:
                std_q = std_answers.get(f"{int(q):02d}", {})
            if not std_q:
                std_q = std_answers.get(str(int(q)), {})
            
            print(f"  Found student answers: {std_q}")
            
            for roman, roman_data in q_data["roman_parts"].items():
                print(f"  Processing roman part {roman}")
                std_roman = std_q.get(roman, "")
                print(f"    Student answer: '{std_roman}'")
                
                if roman_data.get("sub_parts"):
                    print(f"    Has sub-parts: {list(roman_data['sub_parts'].keys())}")
                    for sub, sub_data in roman_data["sub_parts"].items():
                        std_sub = std_roman.get(sub, "") if isinstance(std_roman, dict) else ""
                        print(f"      Sub-part {sub}: '{std_sub}'")
                        print(f"      Rubric: '{sub_data.get('text', '')}'")
                        print(f"      Max marks: {sub_data.get('marks', 1)}")
                        
                        # Test individual grading
                        from Grading import grade_question
                        result = grade_question(f"{q}{roman}{sub}", std_sub, sub_data.get("text", ""), sub_data.get("marks", 1))
                        print(f"      Grading result: {result}")
                        
                        if "error" not in result:
                            score = result.get("score", 0)
                            total_score += score
                            total_max += sub_data.get("marks", 1)
                            feedback_log.append(f"Q{q}{roman}{sub}: {result.get('feedback', '')}")
                            recom_log.append(f"Q{q}{roman}{sub}: {result.get('recommendation', '')}")
                else:
                    print(f"    No sub-parts, direct answer")
                    print(f"    Rubric: '{roman_data.get('text', '')}'")
                    print(f"    Max marks: {roman_data.get('marks', 1)}")
                    
                    # Test individual grading
                    from Grading import grade_question
                    result = grade_question(f"{q}{roman}", std_roman, roman_data.get("text", ""), roman_data.get("marks", 1))
                    print(f"    Grading result: {result}")
                    
                    if "error" not in result:
                        score = result.get("score", 0)
                        total_score += score
                        total_max += roman_data.get("marks", 1)
                        feedback_log.append(f"Q{q}{roman}: {result.get('feedback', '')}")
                        recom_log.append(f"Q{q}{roman}: {result.get('recommendation', '')}")
        
        print(f"\nFinal Results:")
        print(f"Total Score: {total_score}")
        print(f"Total Max: {total_max}")
        print(f"Percentage: {(total_score/total_max*100):.1f}%" if total_max > 0 else "N/A")
        
        # Test the actual grade_student function
        print(f"\nTesting grade_student function...")
        result = grade_student("3992101102", std_answers, ms)
        print(f"grade_student result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run the test"""
    print("GradeMate Final Grading Test")
    print("=" * 50)
    
    test_grading_with_debug()
    
    print("\n" + "=" * 50)
    print("Test completed")
    print("=" * 50)

if __name__ == "__main__":
    main()
