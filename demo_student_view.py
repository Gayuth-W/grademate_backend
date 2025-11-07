#!/usr/bin/env python3
"""
Demo script showing the Student View functionality
This demonstrates what the student view will show when the server is running
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def demo_student_view():
    """Demonstrate the student view functionality"""
    print("🎓 GradeMate Student View Demo")
    print("=" * 50)
    
    try:
        from app.database import SessionLocal
        from app.models import AnswerSheet, GradingResult, MarkingScheme
        
        db = SessionLocal()
        
        # Demo data for student 3992101102
        student_id = "3992101102"
        print(f"📚 Student ID: {student_id}")
        print()
        
        # Get answer sheets for this student
        answer_sheets = db.query(AnswerSheet).filter(
            AnswerSheet.student_id == student_id
        ).all()
        
        if not answer_sheets:
            print("❌ No results found for this student ID")
            return
        
        print(f"✅ Found {len(answer_sheets)} answer sheet(s)")
        print()
        
        # Process each answer sheet
        for i, sheet in enumerate(answer_sheets, 1):
            print(f"📄 Answer Sheet {i}: {sheet.filename}")
            print(f"   Subject: {sheet.subject_id or 'Not specified'}")
            print(f"   Uploaded: {sheet.created_at.strftime('%Y-%m-%d %H:%M')}")
            
            # Get grading results for this sheet
            results = db.query(GradingResult).filter(
                GradingResult.answer_sheet_id == sheet.id
            ).all()
            
            if results:
                for result in results:
                    print(f"   📊 Grade: {result.total_score}/{result.total_max_marks} ({result.percentage:.1f}%)")
                    
                    # Determine grade level
                    if result.percentage >= 80:
                        grade_level = "🟢 Excellent"
                    elif result.percentage >= 60:
                        grade_level = "🟡 Good"
                    elif result.percentage >= 40:
                        grade_level = "🟠 Satisfactory"
                    else:
                        grade_level = "🔴 Needs Improvement"
                    
                    print(f"   🏆 Grade Level: {grade_level}")
                    
                    # Show feedback if available
                    if result.feedback:
                        print(f"   💬 Feedback: {result.feedback[:100]}{'...' if len(str(result.feedback)) > 100 else ''}")
                    
                    # Show recommendations if available
                    if result.recommendations:
                        print(f"   💡 Recommendations: {result.recommendations[:100]}{'...' if len(str(result.recommendations)) > 100 else ''}")
            else:
                print("   ⏳ No grading results yet")
            
            print()
        
        # Show what the API would return
        print("🌐 API Response Preview:")
        print("-" * 30)
        
        all_results = []
        for sheet in answer_sheets:
            grading_results = db.query(GradingResult).filter(
                GradingResult.answer_sheet_id == sheet.id
            ).all()
            
            for result in grading_results:
                result_data = {
                    "id": result.id,
                    "student_id": student_id,
                    "total_score": result.total_score,
                    "total_max_score": result.total_max_marks,
                    "percentage": result.percentage,
                    "created_at": result.created_at.isoformat(),
                    "marking_scheme_name": "Unknown",  # Would be populated from marking scheme
                    "answer_sheet_filename": sheet.filename
                }
                all_results.append(result_data)
        
        print(f"GET /api/student/{student_id}/results")
        print(f"Response: {len(all_results)} result(s)")
        for result in all_results:
            print(f"  - Result {result['id']}: {result['total_score']}/{result['total_max_score']} ({result['percentage']:.1f}%)")
        
        db.close()
        
        print()
        print("✅ Student View Demo Complete!")
        print()
        print("🚀 To use the Student View:")
        print("1. Start the backend server: python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001")
        print("2. Start the frontend: cd ../GradeMate && npm run dev")
        print("3. Go to: http://localhost:5173/student")
        print("4. Enter student ID: 3992101102")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_student_view()
