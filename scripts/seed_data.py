#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import Database
from datetime import datetime, timedelta
import random

def seed_database():
    db = Database()
    
    print("Seeding database with sample data...")
    
    # Sample teachers
    teachers = [
        {'teacher_id': 'T001', 'name': 'Mrs. Sarah Johnson', 'subject': 'Mathematics', 'email': 'sarah.johnson@school.edu', 'phone': '555-0101'},
        {'teacher_id': 'T002', 'name': 'Mr. David Wilson', 'subject': 'Science', 'email': 'david.wilson@school.edu', 'phone': '555-0102'},
        {'teacher_id': 'T003', 'name': 'Ms. Emily Davis', 'subject': 'English', 'email': 'emily.davis@school.edu', 'phone': '555-0103'},
        {'teacher_id': 'T004', 'name': 'Mr. Michael Brown', 'subject': 'History', 'email': 'michael.brown@school.edu', 'phone': '555-0104'},
        {'teacher_id': 'T005', 'name': 'Mrs. Lisa Garcia', 'subject': 'Art', 'email': 'lisa.garcia@school.edu', 'phone': '555-0105'},
        {'teacher_id': 'T006', 'name': 'Mr. Robert Miller', 'subject': 'Physical Education', 'email': 'robert.miller@school.edu', 'phone': '555-0106'},
    ]
    
    for teacher in teachers:
        db.add_teacher(teacher)
    
    # Sample students
    students = [
        {
            'student_id': '12345',
            'name': 'Alex Johnson',
            'class': '10',
            'section': 'A',
            'date_of_birth': '2008-05-15',
            'parent_name': 'John Johnson',
            'parent_email': 'john.johnson@email.com',
            'parent_phone': '555-1001'
        },
        {
            'student_id': '12346',
            'name': 'Emma Wilson',
            'class': '10',
            'section': 'A',
            'date_of_birth': '2008-08-22',
            'parent_name': 'Mary Wilson',
            'parent_email': 'mary.wilson@email.com',
            'parent_phone': '555-1002'
        },
        {
            'student_id': '12347',
            'name': 'Oliver Davis',
            'class': '9',
            'section': 'B',
            'date_of_birth': '2009-03-10',
            'parent_name': 'James Davis',
            'parent_email': 'james.davis@email.com',
            'parent_phone': '555-1003'
        },
        {
            'student_id': '12348',
            'name': 'Sophia Brown',
            'class': '11',
            'section': 'A',
            'date_of_birth': '2007-11-05',
            'parent_name': 'Linda Brown',
            'parent_email': 'linda.brown@email.com',
            'parent_phone': '555-1004'
        },
        {
            'student_id': '12349',
            'name': 'Liam Garcia',
            'class': '8',
            'section': 'C',
            'date_of_birth': '2010-07-18',
            'parent_name': 'Carlos Garcia',
            'parent_email': 'carlos.garcia@email.com',
            'parent_phone': '555-1005'
        }
    ]
    
    for student in students:
        db.add_student(student)
    
    # Create parent authentication accounts
    parent_accounts = [
        {'email': 'john.johnson@email.com', 'password': 'password123', 'student_ids': ['12345']},
        {'email': 'mary.wilson@email.com', 'password': 'password123', 'student_ids': ['12346']},
        {'email': 'james.davis@email.com', 'password': 'password123', 'student_ids': ['12347']},
        {'email': 'linda.brown@email.com', 'password': 'password123', 'student_ids': ['12348']},
        {'email': 'carlos.garcia@email.com', 'password': 'password123', 'student_ids': ['12349']},
    ]
    
    for account in parent_accounts:
        db.create_parent_account(account['email'], account['password'], account['student_ids'])
    
    # Sample class schedule for Class 10-A
    schedule_10a = [
        {'class': '10', 'section': 'A', 'subject': 'Mathematics', 'teacher_id': 'T001', 'day_of_week': 'Monday', 'start_time': '08:00', 'end_time': '09:00', 'room': '101'},
        {'class': '10', 'section': 'A', 'subject': 'Science', 'teacher_id': 'T002', 'day_of_week': 'Monday', 'start_time': '09:00', 'end_time': '10:00', 'room': '102'},
        {'class': '10', 'section': 'A', 'subject': 'English', 'teacher_id': 'T003', 'day_of_week': 'Monday', 'start_time': '10:30', 'end_time': '11:30', 'room': '103'},
        {'class': '10', 'section': 'A', 'subject': 'History', 'teacher_id': 'T004', 'day_of_week': 'Monday', 'start_time': '11:30', 'end_time': '12:30', 'room': '104'},
        {'class': '10', 'section': 'A', 'subject': 'Art', 'teacher_id': 'T005', 'day_of_week': 'Monday', 'start_time': '13:30', 'end_time': '14:30', 'room': '105'},
        
        {'class': '10', 'section': 'A', 'subject': 'Science', 'teacher_id': 'T002', 'day_of_week': 'Tuesday', 'start_time': '08:00', 'end_time': '09:00', 'room': '102'},
        {'class': '10', 'section': 'A', 'subject': 'Mathematics', 'teacher_id': 'T001', 'day_of_week': 'Tuesday', 'start_time': '09:00', 'end_time': '10:00', 'room': '101'},
        {'class': '10', 'section': 'A', 'subject': 'Physical Education', 'teacher_id': 'T006', 'day_of_week': 'Tuesday', 'start_time': '10:30', 'end_time': '11:30', 'room': 'Gym'},
        {'class': '10', 'section': 'A', 'subject': 'English', 'teacher_id': 'T003', 'day_of_week': 'Tuesday', 'start_time': '11:30', 'end_time': '12:30', 'room': '103'},
        {'class': '10', 'section': 'A', 'subject': 'History', 'teacher_id': 'T004', 'day_of_week': 'Tuesday', 'start_time': '13:30', 'end_time': '14:30', 'room': '104'},
        
        {'class': '10', 'section': 'A', 'subject': 'Mathematics', 'teacher_id': 'T001', 'day_of_week': 'Wednesday', 'start_time': '08:00', 'end_time': '09:00', 'room': '101'},
        {'class': '10', 'section': 'A', 'subject': 'English', 'teacher_id': 'T003', 'day_of_week': 'Wednesday', 'start_time': '09:00', 'end_time': '10:00', 'room': '103'},
        {'class': '10', 'section': 'A', 'subject': 'Science', 'teacher_id': 'T002', 'day_of_week': 'Wednesday', 'start_time': '10:30', 'end_time': '11:30', 'room': '102'},
        {'class': '10', 'section': 'A', 'subject': 'Art', 'teacher_id': 'T005', 'day_of_week': 'Wednesday', 'start_time': '11:30', 'end_time': '12:30', 'room': '105'},
        {'class': '10', 'section': 'A', 'subject': 'History', 'teacher_id': 'T004', 'day_of_week': 'Wednesday', 'start_time': '13:30', 'end_time': '14:30', 'room': '104'},
        
        {'class': '10', 'section': 'A', 'subject': 'Science', 'teacher_id': 'T002', 'day_of_week': 'Thursday', 'start_time': '08:00', 'end_time': '09:00', 'room': '102'},
        {'class': '10', 'section': 'A', 'subject': 'Mathematics', 'teacher_id': 'T001', 'day_of_week': 'Thursday', 'start_time': '09:00', 'end_time': '10:00', 'room': '101'},
        {'class': '10', 'section': 'A', 'subject': 'History', 'teacher_id': 'T004', 'day_of_week': 'Thursday', 'start_time': '10:30', 'end_time': '11:30', 'room': '104'},
        {'class': '10', 'section': 'A', 'subject': 'English', 'teacher_id': 'T003', 'day_of_week': 'Thursday', 'start_time': '11:30', 'end_time': '12:30', 'room': '103'},
        {'class': '10', 'section': 'A', 'subject': 'Physical Education', 'teacher_id': 'T006', 'day_of_week': 'Thursday', 'start_time': '13:30', 'end_time': '14:30', 'room': 'Gym'},
        
        {'class': '10', 'section': 'A', 'subject': 'English', 'teacher_id': 'T003', 'day_of_week': 'Friday', 'start_time': '08:00', 'end_time': '09:00', 'room': '103'},
        {'class': '10', 'section': 'A', 'subject': 'Mathematics', 'teacher_id': 'T001', 'day_of_week': 'Friday', 'start_time': '09:00', 'end_time': '10:00', 'room': '101'},
        {'class': '10', 'section': 'A', 'subject': 'Art', 'teacher_id': 'T005', 'day_of_week': 'Friday', 'start_time': '10:30', 'end_time': '11:30', 'room': '105'},
        {'class': '10', 'section': 'A', 'subject': 'Science', 'teacher_id': 'T002', 'day_of_week': 'Friday', 'start_time': '11:30', 'end_time': '12:30', 'room': '102'},
        {'class': '10', 'section': 'A', 'subject': 'History', 'teacher_id': 'T004', 'day_of_week': 'Friday', 'start_time': '13:30', 'end_time': '14:30', 'room': '104'},
    ]
    
    for schedule_item in schedule_10a:
        db.add_schedule(schedule_item)
    
    # Generate sample attendance data for the last 30 days
    student_ids = ['12345', '12346', '12347', '12348', '12349']
    statuses = ['present', 'absent', 'late']
    
    for student_id in student_ids:
        for i in range(30):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            
            # Most days present, some absent or late
            if random.random() < 0.85:  # 85% chance of being present
                status = 'present'
            elif random.random() < 0.8:  # 80% chance of remaining absences being late
                status = 'late'
            else:
                status = 'absent'
            
            reason = 'Sick' if status == 'absent' and random.random() < 0.5 else None
            
            db.add_attendance(student_id, date, status, reason)
    
    # Generate sample grades
    subjects = ['Mathematics', 'Science', 'English', 'History', 'Art']
    test_types = ['Quiz', 'Test', 'Assignment', 'Project', 'Midterm', 'Final']
    
    for student_id in student_ids:
        for subject in subjects:
            # Find the teacher for this subject
            teacher_id = None
            if subject == 'Mathematics':
                teacher_id = 'T001'
            elif subject == 'Science':
                teacher_id = 'T002'
            elif subject == 'English':
                teacher_id = 'T003'
            elif subject == 'History':
                teacher_id = 'T004'
            elif subject == 'Art':
                teacher_id = 'T005'
            
            if teacher_id:
                # Generate 3-5 grades per subject
                for i in range(random.randint(3, 5)):
                    score = random.randint(60, 100)  # Score between 60-100
                    max_score = 100
                    test_type = random.choice(test_types)
                    date = (datetime.now() - timedelta(days=random.randint(1, 60))).strftime('%Y-%m-%d')
                    
                    grade_data = {
                        'student_id': student_id,
                        'subject': subject,
                        'test_type': test_type,
                        'score': score,
                        'max_score': max_score,
                        'date': date,
                        'teacher_id': teacher_id
                    }
                    
                    db.add_grade(grade_data)
    
    print("Database seeding completed successfully!")
    print("\nSample login credentials:")
    print("Email: john.johnson@email.com, Password: password123 (Student ID: 12345)")
    print("Email: mary.wilson@email.com, Password: password123 (Student ID: 12346)")
    print("Email: james.davis@email.com, Password: password123 (Student ID: 12347)")
    print("Email: linda.brown@email.com, Password: password123 (Student ID: 12348)")
    print("Email: carlos.garcia@email.com, Password: password123 (Student ID: 12349)")

if __name__ == '__main__':
    seed_database()