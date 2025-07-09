import sqlite3
import json
import bcrypt
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

class Database:
    def __init__(self, db_path: str = 'data/school.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        tables = [
            """CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                class TEXT NOT NULL,
                section TEXT NOT NULL,
                date_of_birth DATE,
                parent_name TEXT NOT NULL,
                parent_email TEXT NOT NULL,
                parent_phone TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )""",
            
            """CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                subject TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )""",
            
            """CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                date DATE NOT NULL,
                status TEXT CHECK(status IN ('present', 'absent', 'late')) NOT NULL,
                reason TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(student_id)
            )""",
            
            """CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                subject TEXT NOT NULL,
                test_type TEXT NOT NULL,
                score REAL NOT NULL,
                max_score REAL NOT NULL,
                date DATE NOT NULL,
                teacher_id TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(student_id),
                FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
            )""",
            
            """CREATE TABLE IF NOT EXISTS class_schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                class TEXT NOT NULL,
                section TEXT NOT NULL,
                subject TEXT NOT NULL,
                teacher_id TEXT NOT NULL,
                day_of_week TEXT NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                room TEXT,
                FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
            )""",
            
            """CREATE TABLE IF NOT EXISTS parent_auth (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                student_ids TEXT NOT NULL,
                last_login DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )""",
            
            """CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                parent_email TEXT NOT NULL,
                student_id TEXT NOT NULL,
                messages TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )"""
        ]
        
        for table in tables:
            cursor.execute(table)
        
        conn.commit()
        conn.close()
    
    def get_student_by_parent(self, parent_email: str, student_id: str) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT s.*, pa.parent_email 
            FROM students s 
            JOIN parent_auth pa ON pa.parent_email = ? 
            WHERE s.student_id = ? AND pa.student_ids LIKE '%' || ? || '%'
        """
        
        cursor.execute(query, (parent_email, student_id, student_id))
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else None
    
    def get_attendance(self, student_id: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT * FROM attendance 
            WHERE student_id = ? AND date BETWEEN ? AND ?
            ORDER BY date DESC
        """
        
        cursor.execute(query, (student_id, start_date, end_date))
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def get_grades(self, student_id: str, subject: Optional[str] = None) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT g.*, t.name as teacher_name 
            FROM grades g 
            JOIN teachers t ON g.teacher_id = t.teacher_id 
            WHERE g.student_id = ?
        """
        params = [student_id]
        
        if subject:
            query += " AND g.subject = ?"
            params.append(subject)
        
        query += " ORDER BY g.date DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def get_class_schedule(self, class_name: str, section: str) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT cs.*, t.name as teacher_name 
            FROM class_schedule cs 
            JOIN teachers t ON cs.teacher_id = t.teacher_id 
            WHERE cs.class = ? AND cs.section = ?
            ORDER BY cs.day_of_week, cs.start_time
        """
        
        cursor.execute(query, (class_name, section))
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def authenticate_parent(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM parent_auth WHERE parent_email = ?"
        cursor.execute(query, (email,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return None
        
        if bcrypt.checkpw(password.encode('utf-8'), result['password_hash']):
            cursor.execute(
                "UPDATE parent_auth SET last_login = CURRENT_TIMESTAMP WHERE parent_email = ?",
                (email,)
            )
            conn.commit()
            conn.close()
            return dict(result)
        
        conn.close()
        return None
    
    def create_chat_session(self, session_id: str, parent_email: str, student_id: str) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO chat_sessions (session_id, parent_email, student_id, messages)
            VALUES (?, ?, ?, ?)
        """
        
        cursor.execute(query, (session_id, parent_email, student_id, json.dumps([])))
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return session_id
    
    def update_chat_session(self, session_id: str, messages: List[Dict[str, Any]]) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            UPDATE chat_sessions 
            SET messages = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE session_id = ?
        """
        
        cursor.execute(query, (json.dumps(messages), session_id))
        changes = cursor.rowcount
        conn.commit()
        conn.close()
        
        return changes
    
    def create_parent_account(self, email: str, password: str, student_ids: List[str]) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        student_ids_str = ','.join(student_ids)
        
        query = """
            INSERT INTO parent_auth (parent_email, password_hash, student_ids)
            VALUES (?, ?, ?)
        """
        
        cursor.execute(query, (email, password_hash, student_ids_str))
        parent_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return parent_id
    
    def add_student(self, student_data: Dict[str, Any]) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO students (student_id, name, class, section, date_of_birth, 
                                parent_name, parent_email, parent_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(query, (
            student_data['student_id'],
            student_data['name'],
            student_data['class'],
            student_data['section'],
            student_data['date_of_birth'],
            student_data['parent_name'],
            student_data['parent_email'],
            student_data['parent_phone']
        ))
        
        student_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return student_id
    
    def add_teacher(self, teacher_data: Dict[str, Any]) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO teachers (teacher_id, name, subject, email, phone)
            VALUES (?, ?, ?, ?, ?)
        """
        
        cursor.execute(query, (
            teacher_data['teacher_id'],
            teacher_data['name'],
            teacher_data['subject'],
            teacher_data['email'],
            teacher_data['phone']
        ))
        
        teacher_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return teacher_id
    
    def add_attendance(self, student_id: str, date: str, status: str, reason: str = None) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO attendance (student_id, date, status, reason)
            VALUES (?, ?, ?, ?)
        """
        
        cursor.execute(query, (student_id, date, status, reason))
        attendance_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return attendance_id
    
    def add_grade(self, grade_data: Dict[str, Any]) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO grades (student_id, subject, test_type, score, max_score, date, teacher_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(query, (
            grade_data['student_id'],
            grade_data['subject'],
            grade_data['test_type'],
            grade_data['score'],
            grade_data['max_score'],
            grade_data['date'],
            grade_data['teacher_id']
        ))
        
        grade_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return grade_id
    
    def add_schedule(self, schedule_data: Dict[str, Any]) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            INSERT INTO class_schedule (class, section, subject, teacher_id, day_of_week, start_time, end_time, room)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(query, (
            schedule_data['class'],
            schedule_data['section'],
            schedule_data['subject'],
            schedule_data['teacher_id'],
            schedule_data['day_of_week'],
            schedule_data['start_time'],
            schedule_data['end_time'],
            schedule_data['room']
        ))
        
        schedule_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return schedule_id