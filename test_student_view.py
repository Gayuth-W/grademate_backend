#!/usr/bin/env python3
"""
Test script for student view functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_student_endpoints():
    """Test the student view endpoints directly"""
    print("Testing Student View Endpoints")
    print("=" * 50)
    
    try:
        from app.database import SessionLocal
        from app.models import AnswerSheet, GradingResult, MarkingScheme
        
        db = SessionLocal()
        
        # Test 1: Check if we have answer sheets for student 3992101102
        print("1. Checking answer sheets for student 3992101102...")
        answer_sheets = db.query(AnswerSheet).filter(
            AnswerSheet.student_id == "3992101102"
        ).all()
        
        print(f"   Found {len(answer_sheets)} answer sheets")
        for sheet in answer_sheets:
            print(f"   - ID: {sheet.id}, Filename: {sheet.filename}, Marking Scheme ID: {sheet.marking_scheme_id}")
        
        # Test 2: Check grading results for these answer sheets
        print("\n2. Checking grading results...")
        for sheet in answer_sheets:
            results = db.query(GradingResult).filter(
                GradingResult.answer_sheet_id == sheet.id
            ).all()
            print(f"   Answer Sheet {sheet.id}: {len(results)} grading results")
            for result in results:
                print(f"     - Result ID: {result.id}, Score: {result.total_score}/{result.total_max_marks}, Percentage: {result.percentage}%")
        
        # Test 3: Check marking schemes
        print("\n3. Checking marking schemes...")
        marking_schemes = db.query(MarkingScheme).all()
        print(f"   Found {len(marking_schemes)} marking schemes")
        for scheme in marking_schemes:
            print(f"   - ID: {scheme.id}, Filename: {scheme.filename}")
        
        # Test 4: Simulate the student endpoint logic
        print("\n4. Simulating student endpoint logic...")
        student_id = "3992101102"
        
        # Find answer sheets for this student
        student_sheets = db.query(AnswerSheet).filter(
            AnswerSheet.student_id == student_id
        ).all()
        
        if not student_sheets:
            print("   No answer sheets found for student")
        else:
            print(f"   Found {len(student_sheets)} answer sheets for student {student_id}")
            
            # Get grading results for these answer sheets
            all_results = []
            for sheet in student_sheets:
                grading_results = db.query(GradingResult).filter(
                    GradingResult.answer_sheet_id == sheet.id
                ).all()
                
                for result in grading_results:
                    # Get marking scheme details through the answer sheet
                    marking_scheme = None
                    if sheet.marking_scheme_id:
                        marking_scheme = db.query(MarkingScheme).filter(
                            MarkingScheme.id == sheet.marking_scheme_id
                        ).first()
                    
                    result_data = {
                        "id": result.id,
                        "student_id": student_id,
                        "marking_scheme_id": sheet.marking_scheme_id,
                        "answer_sheet_id": result.answer_sheet_id,
                        "total_score": result.total_score,
                        "total_max_score": result.total_max_marks,
                        "percentage": result.percentage,
                        "feedback": result.feedback,
                        "recommendations": result.recommendations,
                        "created_at": result.created_at,
                        "marking_scheme_name": marking_scheme.filename if marking_scheme else "Unknown",
                        "answer_sheet_filename": sheet.filename
                    }
                    all_results.append(result_data)
            
            print(f"   Generated {len(all_results)} result entries")
            for result in all_results:
                print(f"     - Result {result['id']}: {result['total_score']}/{result['total_max_score']} ({result['percentage']:.1f}%) - {result['marking_scheme_name']}")
        
        db.close()
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_student_endpoints()
