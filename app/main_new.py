from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import shutil
from datetime import datetime

# Import our modules
from config import settings
from database import get_db, init_database
from models import MarkingScheme, AnswerSheet, GradingResult, GradingSession
from schemas import (
    BaseResponse, MarkingSchemeResponse, MarkingSchemeDetail,
    AnswerSheetResponse, AnswerSheetDetail, GradingRequest,
    GradingResultResponse, GradingResultDetail, BatchGradingRequest,
    BatchGradingResponse, GradingStatistics, ErrorResponse
)
from services import TextExtractionService, GradingService

app = FastAPI(
    title="GradeMate API", 
    version="1.0.0",
    description="AI-powered grading system for marking schemes and answer sheets"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_database()

# Root endpoints
@app.get("/", response_model=BaseResponse)
async def root():
    """Root endpoint"""
    return BaseResponse(
        success=True,
        message="GradeMate API is running",
        data={"version": "1.0.0", "status": "running"}
    )

@app.get("/health", response_model=BaseResponse)
async def health_check():
    """Health check endpoint"""
    return BaseResponse(
        success=True,
        message="Service is healthy",
        data={
            "status": "healthy",
            "service": "GradeMate API",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Marking Scheme endpoints
@app.post("/api/marking-schemes/upload", response_model=BaseResponse)
async def upload_marking_scheme(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process marking scheme PDF"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed for marking schemes")
        
        # Create uploads directory if it doesn't exist
        uploads_dir = "uploads/marking_schemes"
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(uploads_dir, unique_filename)
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create database record
        marking_scheme = MarkingScheme(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            processing_status="pending"
        )
        db.add(marking_scheme)
        db.commit()
        db.refresh(marking_scheme)
        
        # Process file in background
        background_tasks.add_task(process_marking_scheme_background, marking_scheme.id, file_path)
        
        return BaseResponse(
            success=True,
            message="Marking scheme uploaded successfully",
            data={
                "id": marking_scheme.id,
                "filename": marking_scheme.original_filename,
                "status": "processing"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/marking-schemes", response_model=List[MarkingSchemeResponse])
async def get_marking_schemes(db: Session = Depends(get_db)):
    """Get all marking schemes"""
    marking_schemes = db.query(MarkingScheme).order_by(MarkingScheme.created_at.desc()).all()
    return marking_schemes

@app.get("/api/marking-schemes/{scheme_id}", response_model=MarkingSchemeDetail)
async def get_marking_scheme(scheme_id: int, db: Session = Depends(get_db)):
    """Get specific marking scheme details"""
    marking_scheme = db.query(MarkingScheme).filter(MarkingScheme.id == scheme_id).first()
    if not marking_scheme:
        raise HTTPException(status_code=404, detail="Marking scheme not found")
    return marking_scheme

# Answer Sheet endpoints
@app.post("/api/answer-sheets/upload", response_model=BaseResponse)
async def upload_answer_sheet(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    use_ocr: bool = False,
    db: Session = Depends(get_db)
):
    """Upload and process answer sheet"""
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Only PDF, JPG, JPEG, and PNG files are allowed")
        
        # Create uploads directory if it doesn't exist
        uploads_dir = "uploads/answer_sheets"
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(uploads_dir, unique_filename)
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create database record
        answer_sheet = AnswerSheet(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_format=file_extension[1:],  # Remove the dot
            ocr_used=use_ocr,
            processing_status="pending"
        )
        db.add(answer_sheet)
        db.commit()
        db.refresh(answer_sheet)
        
        # Process file in background
        background_tasks.add_task(process_answer_sheet_background, answer_sheet.id, file_path, use_ocr)
        
        return BaseResponse(
            success=True,
            message="Answer sheet uploaded successfully",
            data={
                "id": answer_sheet.id,
                "filename": answer_sheet.original_filename,
                "status": "processing"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/answer-sheets", response_model=List[AnswerSheetResponse])
async def get_answer_sheets(db: Session = Depends(get_db)):
    """Get all answer sheets"""
    answer_sheets = db.query(AnswerSheet).order_by(AnswerSheet.created_at.desc()).all()
    return answer_sheets

@app.get("/api/answer-sheets/{sheet_id}", response_model=AnswerSheetDetail)
async def get_answer_sheet(sheet_id: int, db: Session = Depends(get_db)):
    """Get specific answer sheet details"""
    answer_sheet = db.query(AnswerSheet).filter(AnswerSheet.id == sheet_id).first()
    if not answer_sheet:
        raise HTTPException(status_code=404, detail="Answer sheet not found")
    return answer_sheet

# Grading endpoints
@app.post("/api/grading/grade", response_model=BaseResponse)
async def grade_answers(
    background_tasks: BackgroundTasks,
    request: GradingRequest,
    db: Session = Depends(get_db)
):
    """Grade answer sheets against a marking scheme"""
    try:
        # Validate marking scheme exists
        marking_scheme = db.query(MarkingScheme).filter(MarkingScheme.id == request.marking_scheme_id).first()
        if not marking_scheme:
            raise HTTPException(status_code=404, detail="Marking scheme not found")
        
        if marking_scheme.processing_status != "completed":
            raise HTTPException(status_code=400, detail="Marking scheme not processed yet")
        
        # Validate answer sheets exist and are processed
        answer_sheets = db.query(AnswerSheet).filter(AnswerSheet.id.in_(request.answer_sheet_ids)).all()
        if len(answer_sheets) != len(request.answer_sheet_ids):
            raise HTTPException(status_code=404, detail="One or more answer sheets not found")
        
        for sheet in answer_sheets:
            if sheet.processing_status != "completed":
                raise HTTPException(status_code=400, detail=f"Answer sheet {sheet.id} not processed yet")
        
        # Start grading in background
        background_tasks.add_task(batch_grade_background, request.marking_scheme_id, request.answer_sheet_ids)
        
        return BaseResponse(
            success=True,
            message="Grading started",
            data={
                "marking_scheme_id": request.marking_scheme_id,
                "answer_sheet_count": len(request.answer_sheet_ids),
                "status": "processing"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Grading failed: {str(e)}")

@app.get("/api/grading/results", response_model=List[GradingResultResponse])
async def get_grading_results(db: Session = Depends(get_db)):
    """Get all grading results"""
    results = db.query(GradingResult).order_by(GradingResult.created_at.desc()).all()
    return results

@app.get("/api/grading/results/{result_id}", response_model=GradingResultDetail)
async def get_grading_result(result_id: int, db: Session = Depends(get_db)):
    """Get specific grading result details"""
    result = db.query(GradingResult).filter(GradingResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Grading result not found")
    return result

@app.get("/api/grading/results/{result_id}/excel")
async def download_excel_result(result_id: int, db: Session = Depends(get_db)):
    """Download Excel file for grading result"""
    result = db.query(GradingResult).filter(GradingResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Grading result not found")
    
    if not result.excel_file_path or not os.path.exists(result.excel_file_path):
        raise HTTPException(status_code=404, detail="Excel file not found")
    
    return FileResponse(
        result.excel_file_path,
        filename=f"grading_result_{result_id}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Statistics endpoint
@app.get("/api/statistics", response_model=GradingStatistics)
async def get_statistics(db: Session = Depends(get_db)):
    """Get system statistics"""
    total_marking_schemes = db.query(MarkingScheme).count()
    total_answer_sheets = db.query(AnswerSheet).count()
    total_grading_results = db.query(GradingResult).count()
    
    # Calculate score statistics
    results = db.query(GradingResult).filter(GradingResult.grading_status == "completed").all()
    scores = [r.percentage for r in results if r.percentage is not None]
    
    stats = GradingStatistics(
        total_marking_schemes=total_marking_schemes,
        total_answer_sheets=total_answer_sheets,
        total_grading_results=total_grading_results,
        average_score=sum(scores) / len(scores) if scores else None,
        highest_score=max(scores) if scores else None,
        lowest_score=min(scores) if scores else None
    )
    
    return stats

# Background task functions
async def process_marking_scheme_background(scheme_id: int, file_path: str):
    """Background task to process marking scheme"""
    from database import SessionLocal
    db = SessionLocal()
    try:
        # Update status to processing
        scheme = db.query(MarkingScheme).filter(MarkingScheme.id == scheme_id).first()
        if scheme:
            scheme.processing_status = "processing"
            db.commit()
            
            # Extract marking scheme
            success, extracted_data, error = TextExtractionService.extract_marking_scheme(file_path)
            
            if success:
                scheme.extracted_data = extracted_data
                scheme.question_count = len(extracted_data)
                # Calculate total marks
                total_marks = 0.0
                for question_data in extracted_data.values():
                    for roman_data in question_data.get("roman_parts", {}).values():
                        if "marks" in roman_data:
                            total_marks += roman_data["marks"]
                        for subpart_data in roman_data.get("sub_parts", {}).values():
                            if "marks" in subpart_data:
                                total_marks += subpart_data["marks"]
                scheme.total_marks = total_marks
                scheme.processing_status = "completed"
            else:
                scheme.processing_status = "failed"
                scheme.error_message = error
            
            db.commit()
    finally:
        db.close()

async def process_answer_sheet_background(sheet_id: int, file_path: str, use_ocr: bool):
    """Background task to process answer sheet"""
    from database import SessionLocal
    db = SessionLocal()
    try:
        # Update status to processing
        sheet = db.query(AnswerSheet).filter(AnswerSheet.id == sheet_id).first()
        if sheet:
            sheet.processing_status = "processing"
            db.commit()
            
            # Extract answers
            success, extracted_data, error = TextExtractionService.extract_answer_sheet(file_path, use_ocr)
            
            if success:
                sheet.student_id = extracted_data.get("student_id")
                sheet.subject_id = extracted_data.get("subject_id")
                sheet.page_no = extracted_data.get("page_no")
                sheet.extracted_answers = extracted_data.get("answers")
                sheet.processing_status = "completed"
            else:
                sheet.processing_status = "failed"
                sheet.error_message = error
            
            db.commit()
    finally:
        db.close()

async def batch_grade_background(marking_scheme_id: int, answer_sheet_ids: list):
    """Background task to grade multiple answer sheets"""
    from database import SessionLocal
    db = SessionLocal()
    try:
        success, results, error = GradingService.batch_grade_answer_sheets(
            db, marking_scheme_id, answer_sheet_ids
        )
        if not success:
            print(f"Batch grading failed: {error}")
    finally:
        db.close()
