from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

# Base schemas
class BaseResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# Marking Scheme schemas
class MarkingSchemeUpload(BaseModel):
    filename: str
    file_path: str

class MarkingSchemeResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    question_count: int
    total_marks: float
    processing_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class MarkingSchemeDetail(MarkingSchemeResponse):
    extracted_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

# Answer Sheet schemas
class AnswerSheetUpload(BaseModel):
    filename: str
    file_path: str
    file_format: str
    use_ocr: bool = False

class AnswerSheetResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_format: str
    student_id: Optional[str] = None
    subject_id: Optional[str] = None
    processing_status: str
    ocr_used: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class AnswerSheetDetail(AnswerSheetResponse):
    extracted_answers: Optional[str] = None
    parsed_answers: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    marking_scheme_id: Optional[int] = None

# Grading schemas
class GradingRequest(BaseModel):
    marking_scheme_id: int
    answer_sheet_ids: List[int]

class GradingResultResponse(BaseModel):
    id: int
    student_id: Optional[str] = None
    total_score: float
    total_max_marks: float
    percentage: float
    grading_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class GradingResultDetail(GradingResultResponse):
    question_scores: Optional[Dict[str, float]] = None
    feedback: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    excel_file_path: Optional[str] = None
    feedback_file_path: Optional[str] = None
    recommendations_file_path: Optional[str] = None
    error_message: Optional[str] = None

# Student View Schemas
class StudentGradingResultResponse(BaseModel):
    id: int
    student_id: str
    marking_scheme_id: Optional[int] = None
    answer_sheet_id: int
    total_score: float
    total_max_score: float
    percentage: float
    feedback: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    created_at: datetime
    marking_scheme_name: str
    answer_sheet_filename: str
    
    class Config:
        from_attributes = True

class StudentGradingResultDetail(StudentGradingResultResponse):
    detailed_results: Optional[Dict[str, Any]] = None

# File processing schemas
class FileProcessingStatus(BaseModel):
    file_id: int
    file_type: str  # "marking_scheme" or "answer_sheet"
    status: str
    progress: Optional[int] = None
    message: Optional[str] = None

# Batch operations
class BatchGradingRequest(BaseModel):
    marking_scheme_id: int
    answer_sheet_ids: List[int]
    session_name: Optional[str] = None

class BatchGradingResponse(BaseModel):
    session_id: int
    total_files: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Statistics schemas
class GradingStatistics(BaseModel):
    total_marking_schemes: int
    total_answer_sheets: int
    total_grading_results: int
    average_score: Optional[float] = None
    highest_score: Optional[float] = None
    lowest_score: Optional[float] = None

# Error schemas
class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None
