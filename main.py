from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import logging
import uuid

from models.database import Database
from models.schemas import (
    LoginRequest, LoginResponse, ChatSessionRequest, ChatSessionResponse,
    ChatMessageRequest, ChatMessageResponse, StudentInfo, AttendanceResponse,
    GradeResponse, ScheduleResponse, HealthResponse, ErrorResponse
)
from auth.auth import create_access_token, verify_password, get_current_user
from chatbot.school_bot import SchoolBot

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SchoolBot API",
    description="A secure chatbot system for school parent-teacher interactions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize database and chatbot
db = Database()
school_bot = SchoolBot()

# Templates
templates = Jinja2Templates(directory="templates")

# Serve static files
app.mount("/static", StaticFiles(directory="templates"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/auth/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login(request: Request, login_data: LoginRequest):
    try:
        user = db.authenticate_parent(login_data.email, login_data.password)
        
        if user:
            access_token = create_access_token(
                data={"sub": login_data.email, "student_ids": user['student_ids']}
            )
            return LoginResponse(
                access_token=access_token,
                student_ids=user['student_ids'].split(','),
                message="Login successful"
            )
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/chat/session", response_model=ChatSessionResponse)
@limiter.limit("10/minute")
async def create_chat_session(
    request: Request,
    session_data: ChatSessionRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        session_id = str(uuid.uuid4())
        
        db.create_chat_session(session_id, current_user["sub"], session_data.student_id)
        
        return ChatSessionResponse(
            session_id=session_id,
            message="Chat session created successfully"
        )
        
    except Exception as e:
        logger.error(f"Create session error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/chat/message", response_model=ChatMessageResponse)
@limiter.limit("30/minute")
async def send_message(
    request: Request,
    message_data: ChatMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        response = school_bot.process_message(
            message_data.session_id,
            current_user["sub"],
            message_data.message
        )
        
        return ChatMessageResponse(
            response=response,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Send message error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/student/info", response_model=StudentInfo)
async def get_student_info(
    student_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        student = db.get_student_by_parent(current_user["sub"], student_id)
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found or access denied")
        
        return StudentInfo(
            student_id=student['student_id'],
            name=student['name'],
            class_name=student['class'],
            section=student['section']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get student info error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/student/attendance", response_model=AttendanceResponse)
async def get_attendance(
    student_id: str,
    start_date: str = None,
    end_date: str = None,
    current_user: dict = Depends(get_current_user)
):
    try:
        student = db.get_student_by_parent(current_user["sub"], student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found or access denied")
        
        if not start_date or not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        attendance = db.get_attendance(student_id, start_date, end_date)
        
        summary = {
            "total_days": len(attendance),
            "present": len([a for a in attendance if a['status'] == 'present']),
            "absent": len([a for a in attendance if a['status'] == 'absent']),
            "late": len([a for a in attendance if a['status'] == 'late'])
        }
        
        return AttendanceResponse(attendance=attendance, summary=summary)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get attendance error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/student/grades", response_model=GradeResponse)
async def get_grades(
    student_id: str,
    subject: str = None,
    current_user: dict = Depends(get_current_user)
):
    try:
        student = db.get_student_by_parent(current_user["sub"], student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found or access denied")
        
        grades = db.get_grades(student_id, subject)
        
        return GradeResponse(grades=grades)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get grades error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/student/schedule", response_model=ScheduleResponse)
async def get_schedule(
    student_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        student = db.get_student_by_parent(current_user["sub"], student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found or access denied")
        
        schedule = db.get_class_schedule(student['class'], student['section'])
        
        # Convert 'class' field to 'class_name' for the response
        for item in schedule:
            item['class_name'] = item.pop('class', '')
        
        return ScheduleResponse(schedule=schedule)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get schedule error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0"
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return {"error": "Endpoint not found"}

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: HTTPException):
    logger.error(f"Internal server error: {str(exc)}")
    return {"error": "Internal server error"}

if __name__ == "__main__":
    import uvicorn
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )