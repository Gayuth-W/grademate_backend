import os
import json
import tempfile
import shutil
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from .models import MarkingScheme, AnswerSheet, GradingResult
from . import markingextractor
from . import newocr
from .Grading import grade_student, parse_misc
from . import text_extraction_fallback
import logging

logger = logging.getLogger(__name__)

class TextExtractionService:
    """Service for extracting text from uploaded files"""
    
    @staticmethod
    def extract_marking_scheme(file_path: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract marking scheme from PDF file
        Returns: (success, extracted_data, error_message)
        """
        try:
            logger.info(f"Extracting marking scheme from: {file_path}")
            
            # Try Google Vision API first
            try:
                marking_scheme = markingextractor.process_marking_scheme_pdf(file_path)
                if marking_scheme:
                    logger.info("Successfully extracted using Google Vision API")
                    return TextExtractionService._process_marking_scheme_data(marking_scheme)
            except Exception as e:
                logger.warning(f"Google Vision API failed: {e}")
            
            # Fallback to PyMuPDF extraction
            logger.info("Falling back to PyMuPDF extraction")
            marking_scheme = text_extraction_fallback.extract_marking_scheme_fallback(file_path)
            if marking_scheme:
                logger.info("Successfully extracted using fallback method")
                return TextExtractionService._process_marking_scheme_data(marking_scheme)
            else:
                return False, None, "Failed to extract marking scheme structure with both methods"
                
        except Exception as e:
            logger.error(f"Error extracting marking scheme: {e}")
            return False, None, str(e)
    
    @staticmethod
    def _process_marking_scheme_data(marking_scheme: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Process extracted marking scheme data"""
        try:
            # Calculate question count and total marks
            question_count = len(marking_scheme)
            total_marks = 0.0
            
            for question_data in marking_scheme.values():
                for roman_data in question_data.get("roman_parts", {}).values():
                    # Add roman part marks
                    if "marks" in roman_data:
                        total_marks += roman_data["marks"]
                    
                    # Add sub-part marks
                    for subpart_data in roman_data.get("sub_parts", {}).values():
                        if "marks" in subpart_data:
                            total_marks += subpart_data["marks"]
            
            logger.info(f"Successfully processed marking scheme: {question_count} questions, {total_marks} total marks")
            return True, marking_scheme, None
        except Exception as e:
            logger.error(f"Error processing marking scheme data: {e}")
            return False, None, str(e)
    
    @staticmethod
    def extract_answer_sheet(file_path: str, use_ocr: bool = False) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Extract answers from answer sheet file
        Returns: (success, extracted_data, error_message)
        """
        try:
            logger.info(f"Extracting answers from: {file_path}, OCR: {use_ocr}")
            
            # Try Google Vision API first
            try:
                result = newocr.process_file(file_path)
                if result:
                    extracted_data = {
                        "student_id": result.get("student_id"),
                        "subject_id": result.get("subject_id"),
                        "page_no": result.get("page_no"),
                        "answers": result.get("answers"),
                        "file_processed": result.get("file_processed"),
                        "file_format": result.get("file_format")
                    }
                    logger.info("Successfully extracted using Google Vision API")
                    logger.info(f"Student ID: {result.get('student_id')}")
                    return True, extracted_data, None
            except Exception as e:
                logger.warning(f"Google Vision API failed: {e}")
            
            # Fallback to PyMuPDF/Tesseract extraction
            logger.info("Falling back to PyMuPDF/Tesseract extraction")
            result = text_extraction_fallback.extract_answer_sheet_fallback(file_path)
            if result:
                logger.info("Successfully extracted using fallback method")
                logger.info(f"Student ID: {result.get('student_id')}")
                return True, result, None
            else:
                return False, None, "Failed to extract answers from file with both methods"
                
        except Exception as e:
            logger.error(f"Error extracting answers: {e}")
            return False, None, str(e)

class GradingService:
    """Service for grading answer sheets against marking schemes"""
    
    @staticmethod
    def grade_answer_sheet(
        db: Session, 
        marking_scheme_id: int, 
        answer_sheet_id: int
    ) -> Tuple[bool, Optional[GradingResult], Optional[str]]:
        """
        Grade a single answer sheet against a marking scheme
        Returns: (success, grading_result, error_message)
        """
        try:
            logger.info(f"Grading answer sheet {answer_sheet_id} against marking scheme {marking_scheme_id}")
            
            # Get marking scheme and answer sheet from database
            marking_scheme = db.query(MarkingScheme).filter(MarkingScheme.id == marking_scheme_id).first()
            answer_sheet = db.query(AnswerSheet).filter(AnswerSheet.id == answer_sheet_id).first()
            
            if not marking_scheme:
                return False, None, "Marking scheme not found"
            
            if not answer_sheet:
                return False, None, "Answer sheet not found"
            
            if not marking_scheme.extracted_data:
                return False, None, "Marking scheme not processed yet"
            
            if not answer_sheet.extracted_answers:
                return False, None, "Answer sheet not processed yet"
            
            # Create temporary files for grading process
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write marking scheme to temporary file
                marking_scheme_file = os.path.join(temp_dir, "marking_scheme_extracted.json")
                with open(marking_scheme_file, 'w', encoding='utf-8') as f:
                    json.dump(marking_scheme.extracted_data, f, indent=2, ensure_ascii=False)
                
                # Write answer sheet data to temporary file
                answer_sheet_data = {
                    "student_id": answer_sheet.student_id,
                    "answers": answer_sheet.extracted_answers
                }
                answer_sheet_file = os.path.join(temp_dir, "output_questions2.json")
                with open(answer_sheet_file, 'w', encoding='utf-8') as f:
                    json.dump(answer_sheet_data, f, indent=2, ensure_ascii=False)
                
                # Change to temp directory for grading
                original_cwd = os.getcwd()
                os.chdir(temp_dir)
                
                try:
                    # Parse student answers
                    std_answers = parse_misc(answer_sheet.extracted_answers)
                    
                    # Create grading result record
                    grading_result = GradingResult(
                        answer_sheet_id=answer_sheet_id,
                        student_id=answer_sheet.student_id,
                        grading_status="processing"
                    )
                    db.add(grading_result)
                    db.commit()
                    db.refresh(grading_result)
                    
                    # Perform grading
                    total_score = 0.0
                    total_max = 0.0
                    feedback_log = []
                    recom_log = []
                    question_scores = {}
                    
                    for q, q_data in marking_scheme.extracted_data.items():
                        std_q = std_answers.get(q, {})
                        
                        for roman, roman_data in q_data["roman_parts"].items():
                            std_roman = std_q.get(roman, "")
                            
                            if roman_data.get("sub_parts"):
                                for sub, sub_data in roman_data["sub_parts"].items():
                                    std_sub = std_roman.get(sub, "") if isinstance(std_roman, dict) else ""
                                    rubric_text = sub_data.get("text", "")
                                    max_mark = sub_data.get("marks", 1)
                                    total_max += max_mark
                                    
                                    # Grade the question part
                                    from .Grading import grade_question
                                    result = grade_question(f"{q}{roman}{sub}", std_sub, rubric_text, max_mark)
                                    
                                    if "error" in result:
                                        feedback_log.append(f"Q{q}{roman}{sub}: {result['error']}")
                                        recom_log.append(f"Q{q}{roman}{sub}: No recommendations (parse error)")
                                        question_scores[f"{q}{roman}{sub}"] = 0.0
                                    else:
                                        score = result.get("score", 0)
                                        total_score += score
                                        question_scores[f"{q}{roman}{sub}"] = score
                                        feedback_log.append(f"Q{q}{roman}{sub}: {result.get('feedback', '')}")
                                        recom_log.append(f"Q{q}{roman}{sub}: {result.get('recommendation', '')}")
                            else:
                                rubric_text = roman_data.get("text", "")
                                max_mark = roman_data.get("marks", 1)
                                total_max += max_mark
                                
                                from .Grading import grade_question
                                result = grade_question(f"{q}{roman}", std_roman, rubric_text, max_mark)
                                
                                if "error" in result:
                                    feedback_log.append(f"Q{q}{roman}: {result['error']}")
                                    recom_log.append(f"Q{q}{roman}: No recommendations (parse error)")
                                    question_scores[f"{q}{roman}"] = 0.0
                                else:
                                    score = result.get("score", 0)
                                    total_score += score
                                    question_scores[f"{q}{roman}"] = score
                                    feedback_log.append(f"Q{q}{roman}: {result.get('feedback', '')}")
                                    recom_log.append(f"Q{q}{roman}: {result.get('recommendation', '')}")
                    
                    # Calculate percentage
                    percentage = (total_score / total_max * 100) if total_max > 0 else 0.0
                    
                    # Update grading result
                    grading_result.total_score = total_score
                    grading_result.total_max_marks = total_max
                    grading_result.percentage = percentage
                    grading_result.question_scores = question_scores
                    grading_result.feedback = feedback_log
                    grading_result.recommendations = recom_log
                    grading_result.grading_status = "completed"
                    
                    # Save generated files
                    results_dir = os.path.join(original_cwd, "results")
                    os.makedirs(results_dir, exist_ok=True)
                    
                    # Save Excel file
                    excel_file = os.path.join(results_dir, f"results_{grading_result.id}.xlsx")
                    import pandas as pd
                    df = pd.DataFrame([{
                        "student_id": answer_sheet.student_id,
                        "score": f"{total_score}/{total_max}",
                        "percentage": f"{percentage:.2f}%"
                    }])
                    df.to_excel(excel_file, index=False)
                    grading_result.excel_file_path = excel_file
                    
                    # Save feedback file
                    feedback_file = os.path.join(results_dir, f"feedback_{grading_result.id}.txt")
                    with open(feedback_file, "w", encoding="utf-8") as f:
                        f.write("\n".join(feedback_log))
                    grading_result.feedback_file_path = feedback_file
                    
                    # Save recommendations file
                    recommendations_file = os.path.join(results_dir, f"recommendations_{grading_result.id}.txt")
                    with open(recommendations_file, "w", encoding="utf-8") as f:
                        f.write("\n".join(recom_log))
                    grading_result.recommendations_file_path = recommendations_file
                    
                    db.commit()
                    db.refresh(grading_result)
                    
                    logger.info(f"Successfully graded answer sheet: {total_score}/{total_max} ({percentage:.2f}%)")
                    return True, grading_result, None
                    
                finally:
                    os.chdir(original_cwd)
                    
        except Exception as e:
            logger.error(f"Error grading answer sheet: {e}")
            return False, None, str(e)
    
    @staticmethod
    def batch_grade_answer_sheets(
        db: Session, 
        marking_scheme_id: int, 
        answer_sheet_ids: list
    ) -> Tuple[bool, list, Optional[str]]:
        """
        Grade multiple answer sheets against a marking scheme
        Returns: (success, grading_results, error_message)
        """
        try:
            logger.info(f"Batch grading {len(answer_sheet_ids)} answer sheets against marking scheme {marking_scheme_id}")
            
            grading_results = []
            for answer_sheet_id in answer_sheet_ids:
                success, result, error = GradingService.grade_answer_sheet(db, marking_scheme_id, answer_sheet_id)
                if success:
                    grading_results.append(result)
                else:
                    logger.error(f"Failed to grade answer sheet {answer_sheet_id}: {error}")
            
            logger.info(f"Batch grading completed: {len(grading_results)}/{len(answer_sheet_ids)} successful")
            return True, grading_results, None
            
        except Exception as e:
            logger.error(f"Error in batch grading: {e}")
            return False, [], str(e)
