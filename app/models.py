from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class MarkingScheme(Base):
    """Table to store marking scheme data"""
    __tablename__ = "marking_schemes"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    extracted_data = Column(JSON, nullable=True)  # Store the structured marking scheme
    question_count = Column(Integer, default=0)
    total_marks = Column(Float, default=0.0)
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to answer sheets that use this marking scheme
    answer_sheets = relationship("AnswerSheet", back_populates="marking_scheme")

class AnswerSheet(Base):
    """Table to store answer sheet data"""
    __tablename__ = "answer_sheets"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_format = Column(String(10), nullable=False)  # pdf, jpg, png, jpeg
    
    # Extracted data
    student_id = Column(String(100), nullable=True)
    subject_id = Column(String(100), nullable=True)
    page_no = Column(String(20), nullable=True)
    extracted_answers = Column(Text, nullable=True)  # Raw extracted text
    parsed_answers = Column(JSON, nullable=True)  # Structured answers
    
    # Processing status
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    ocr_used = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    
    # Relationship to marking scheme
    marking_scheme_id = Column(Integer, ForeignKey("marking_schemes.id"), nullable=True)
    marking_scheme = relationship("MarkingScheme", back_populates="answer_sheets")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to grading results
    grading_results = relationship("GradingResult", back_populates="answer_sheet")

class GradingResult(Base):
    """Table to store grading results"""
    __tablename__ = "grading_results"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships
    answer_sheet_id = Column(Integer, ForeignKey("answer_sheets.id"), nullable=False)
    answer_sheet = relationship("AnswerSheet", back_populates="grading_results")
    
    # Grading data
    student_id = Column(String(100), nullable=True)
    total_score = Column(Float, default=0.0)
    total_max_marks = Column(Float, default=0.0)
    percentage = Column(Float, default=0.0)
    
    # Detailed results
    question_scores = Column(JSON, nullable=True)  # {"1i": 2.0, "1ii": 1.5, ...}
    feedback = Column(JSON, nullable=True)  # List of feedback strings
    recommendations = Column(JSON, nullable=True)  # List of recommendation strings
    
    # File paths for generated files
    excel_file_path = Column(String(500), nullable=True)
    feedback_file_path = Column(String(500), nullable=True)
    recommendations_file_path = Column(String(500), nullable=True)
    
    # Status
    grading_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GradingSession(Base):
    """Table to track grading sessions (when multiple answer sheets are graded together)"""
    __tablename__ = "grading_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_name = Column(String(255), nullable=True)
    marking_scheme_id = Column(Integer, ForeignKey("marking_schemes.id"), nullable=False)
    marking_scheme = relationship("MarkingScheme")
    
    # Session data
    total_answer_sheets = Column(Integer, default=0)
    processed_answer_sheets = Column(Integer, default=0)
    session_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    
    # Results summary
    average_score = Column(Float, default=0.0)
    highest_score = Column(Float, default=0.0)
    lowest_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
