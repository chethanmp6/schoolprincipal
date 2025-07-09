from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    student_ids: List[str]
    message: str

class ChatSessionRequest(BaseModel):
    student_id: str

class ChatSessionResponse(BaseModel):
    session_id: str
    message: str

class ChatMessageRequest(BaseModel):
    session_id: str
    message: str

class ChatMessageResponse(BaseModel):
    response: str
    timestamp: datetime

class StudentInfo(BaseModel):
    student_id: str
    name: str
    class_name: str = ""
    section: str
    
    class Config:
        from_attributes = True

class AttendanceRecord(BaseModel):
    id: int
    student_id: str
    date: str
    status: str
    reason: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class AttendanceSummary(BaseModel):
    total_days: int
    present: int
    absent: int
    late: int

class AttendanceResponse(BaseModel):
    attendance: List[AttendanceRecord]
    summary: AttendanceSummary

class Grade(BaseModel):
    id: int
    student_id: str
    subject: str
    test_type: str
    score: float
    max_score: float
    date: str
    teacher_id: str
    teacher_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class GradeResponse(BaseModel):
    grades: List[Grade]

class ScheduleItem(BaseModel):
    id: int
    class_name: str = ""
    section: str
    subject: str
    teacher_id: str
    teacher_name: str
    day_of_week: str
    start_time: str
    end_time: str
    room: Optional[str] = None
    
    class Config:
        from_attributes = True

class ScheduleResponse(BaseModel):
    schedule: List[ScheduleItem]

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str

class ErrorResponse(BaseModel):
    error: str