import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from models.database import Database

class SchoolBot:
    def __init__(self):
        self.db = Database()
        self.conversation_context = {}
    
    def process_message(self, session_id: str, parent_email: str, message: str) -> str:
        try:
            if session_id not in self.conversation_context:
                self.conversation_context[session_id] = {
                    'parent_email': parent_email,
                    'is_authenticated': False,
                    'current_student': None,
                    'conversation_history': []
                }
            
            context = self.conversation_context[session_id]
            context['conversation_history'].append({
                'role': 'user',
                'content': message,
                'timestamp': datetime.now().isoformat()
            })
            
            response = self._generate_response(context, message)
            
            context['conversation_history'].append({
                'role': 'assistant',
                'content': response,
                'timestamp': datetime.now().isoformat()
            })
            
            self.db.update_chat_session(session_id, context['conversation_history'])
            
            return response
            
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            return "I apologize, but I encountered an error processing your request. Please try again or contact the school office for assistance."
    
    def _generate_response(self, context: Dict[str, Any], message: str) -> str:
        lower_message = message.lower()
        
        if not context['is_authenticated']:
            return self._handle_authentication(context, message)
        
        if self._is_greeting(lower_message):
            return self._generate_greeting(context)
        
        if self._is_attendance_query(lower_message):
            return self._handle_attendance_query(context, message)
        
        if self._is_grade_query(lower_message):
            return self._handle_grade_query(context, message)
        
        if self._is_schedule_query(lower_message):
            return self._handle_schedule_query(context, message)
        
        if self._is_teacher_query(lower_message):
            return self._handle_teacher_query(context, message)
        
        if self._is_general_school_query(lower_message):
            return self._handle_general_school_query(context, message)
        
        return self._generate_help_response()
    
    def _handle_authentication(self, context: Dict[str, Any], message: str) -> str:
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        student_id_pattern = r'\b\d{4,}\b'
        
        email_match = re.search(email_pattern, message)
        student_id_match = re.search(student_id_pattern, message)
        
        if not email_match or not student_id_match:
            return """🔐 **Authentication Required**

To access your child's information, please provide:
- Your registered email address
- Your child's student ID

Example: "My email is parent@email.com and my child's ID is 12345"

This ensures we maintain the privacy and security of student data."""
        
        context['parent_email'] = email_match.group()
        context['current_student'] = student_id_match.group()
        context['is_authenticated'] = True
        
        return """✅ **Welcome to SchoolBot!**

Hello! I'm here to help you access information about your child's academic progress.

**What I can help you with:**
📊 **Attendance**: Check attendance records and statistics
📚 **Grades**: View test scores and academic performance
📅 **Schedule**: Get class timetables and exam dates
👨‍🏫 **Teachers**: Find teacher information and contact details
ℹ️ **School Info**: General school policies and procedures

**How to get started:**
- Ask about attendance: "Show me attendance for this month"
- Check grades: "What are the latest test scores?"
- View schedule: "What's the class schedule for today?"

What would you like to know about your child's education?"""
    
    def _handle_attendance_query(self, context: Dict[str, Any], message: str) -> str:
        try:
            student = self.db.get_student_by_parent(context['parent_email'], context['current_student'])
            
            if not student:
                return "❌ I couldn't find a student record associated with your account. Please verify your student ID and try again."
            
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            attendance = self.db.get_attendance(context['current_student'], start_date, end_date)
            
            total_days = len(attendance)
            present_days = len([a for a in attendance if a['status'] == 'present'])
            absent_days = len([a for a in attendance if a['status'] == 'absent'])
            late_days = len([a for a in attendance if a['status'] == 'late'])
            
            attendance_percentage = round((present_days / total_days) * 100) if total_days > 0 else 0
            
            recent_absences = [a['date'] for a in attendance if a['status'] == 'absent'][:5]
            
            response = f"""📊 **Attendance Report for {student['name']}** - Class {student['class']}-{student['section']}

**Current Month Statistics:**
- 📈 **Attendance Rate**: {attendance_percentage}%
- ✅ **Days Present**: {present_days}
- ❌ **Days Absent**: {absent_days}
- ⏰ **Days Late**: {late_days}
- 📅 **Total School Days**: {total_days}

{f"**Recent Absences**: {', '.join(recent_absences)}" if recent_absences else "**No recent absences** ✨"}

ℹ️ **Note**: School policy requires minimum 75% attendance for academic progression.

Need more details about specific dates or have questions about attendance policies?"""
            
            return response
            
        except Exception as e:
            print(f"Error handling attendance query: {str(e)}")
            return "❌ I encountered an error retrieving attendance information. Please try again or contact the school office."
    
    def _handle_grade_query(self, context: Dict[str, Any], message: str) -> str:
        try:
            student = self.db.get_student_by_parent(context['parent_email'], context['current_student'])
            
            if not student:
                return "❌ I couldn't find a student record associated with your account. Please verify your student ID and try again."
            
            subject_pattern = r'\b(math|science|english|history|geography|physics|chemistry|biology|computer|art|music|pe|physical education)\b'
            subject_match = re.search(subject_pattern, message, re.IGNORECASE)
            subject = subject_match.group() if subject_match else None
            
            grades = self.db.get_grades(context['current_student'], subject)
            
            if not grades:
                return f"""📚 **Academic Performance - {student['name']}**

No grades found{f' for {subject}' if subject else ''} in our current records.

This might be because:
- No tests have been conducted yet this term
- Grades haven't been updated by teachers
- The subject name might be different

Please contact your class teacher for more information."""
            
            subject_groups = {}
            for grade in grades:
                if grade['subject'] not in subject_groups:
                    subject_groups[grade['subject']] = []
                subject_groups[grade['subject']].append(grade)
            
            response = f"📚 **Academic Performance - {student['name']}**\n\n"
            
            for subject_name, subject_grades in subject_groups.items():
                latest_grade = subject_grades[0]
                average = sum(g['score'] / g['max_score'] * 100 for g in subject_grades) / len(subject_grades)
                
                response += f"**{subject_name.upper()}**\n"
                response += f"- 📝 **Latest Test**: {latest_grade['score']}/{latest_grade['max_score']} ({round(latest_grade['score']/latest_grade['max_score']*100)}%)\n"
                response += f"- 📊 **Term Average**: {round(average)}%\n"
                response += f"- 👨‍🏫 **Teacher**: {latest_grade['teacher_name']}\n"
                response += f"- 📅 **Last Updated**: {latest_grade['date']}\n\n"
            
            overall_average = sum(g['score'] / g['max_score'] * 100 for g in grades) / len(grades)
            response += f"📈 **Overall Performance**: {round(overall_average)}%\n\n"
            
            if overall_average < 60:
                response += "🎯 **Areas for Improvement**: Performance below 60% indicates need for additional support. Consider speaking with teachers about tutoring options.\n\n"
            
            response += "Need more details about specific subjects or test dates?"
            
            return response
            
        except Exception as e:
            print(f"Error handling grade query: {str(e)}")
            return "❌ I encountered an error retrieving grade information. Please try again or contact the school office."
    
    def _handle_schedule_query(self, context: Dict[str, Any], message: str) -> str:
        try:
            student = self.db.get_student_by_parent(context['parent_email'], context['current_student'])
            
            if not student:
                return "❌ I couldn't find a student record associated with your account. Please verify your student ID and try again."
            
            schedule = self.db.get_class_schedule(student['class'], student['section'])
            
            if not schedule:
                return f"""📅 **Class Schedule - {student['class']}-{student['section']}**

No schedule information available in our current records.

Please contact the school office for the latest timetable information."""
            
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
            response = f"📅 **Class Schedule for {student['class']}-{student['section']}**\n\n"
            
            for day in days:
                day_schedule = [s for s in schedule if s['day_of_week'].lower() == day.lower()]
                if day_schedule:
                    response += f"**{day}**\n"
                    day_schedule.sort(key=lambda x: x['start_time'])
                    for period in day_schedule:
                        room_info = f" | Room {period['room']}" if period['room'] else ""
                        response += f"{period['start_time']} - {period['end_time']} | {period['subject']} | {period['teacher_name']}{room_info}\n"
                    response += "\n"
            
            response += "📞 **Need to contact a teacher?** Ask me for teacher contact information!\n"
            response += "📚 **Want to know about upcoming tests?** I can help with exam schedules too!"
            
            return response
            
        except Exception as e:
            print(f"Error handling schedule query: {str(e)}")
            return "❌ I encountered an error retrieving schedule information. Please try again or contact the school office."
    
    def _handle_teacher_query(self, context: Dict[str, Any], message: str) -> str:
        try:
            student = self.db.get_student_by_parent(context['parent_email'], context['current_student'])
            
            if not student:
                return "❌ I couldn't find a student record associated with your account. Please verify your student ID and try again."
            
            schedule = self.db.get_class_schedule(student['class'], student['section'])
            
            if not schedule:
                return f"""👨‍🏫 **Teacher Information**

No teacher information available in our current records for class {student['class']}-{student['section']}.

Please contact the school office for teacher contact details."""
            
            teachers = {}
            for s in schedule:
                if s['teacher_id'] not in teachers:
                    teachers[s['teacher_id']] = {
                        'name': s['teacher_name'],
                        'subjects': set()
                    }
                teachers[s['teacher_id']]['subjects'].add(s['subject'])
            
            response = f"👨‍🏫 **Teacher Information for Class {student['class']}-{student['section']}**\n\n"
            
            for teacher in teachers.values():
                response += f"**{teacher['name']}**\n"
                response += f"- 📚 **Subjects**: {', '.join(teacher['subjects'])}\n"
                response += f"- 📞 **Contact**: Available through school office\n"
                response += f"- 📧 **Email**: Contact school office for email address\n\n"
            
            response += "📞 **School Office Contact**: For direct teacher contact information\n"
            response += "⏰ **Office Hours**: Monday-Friday, 8:00 AM - 4:00 PM\n\n"
            response += "💡 **Tip**: For parent-teacher meetings, please contact the school office to schedule appointments."
            
            return response
            
        except Exception as e:
            print(f"Error handling teacher query: {str(e)}")
            return "❌ I encountered an error retrieving teacher information. Please try again or contact the school office."
    
    def _handle_general_school_query(self, context: Dict[str, Any], message: str) -> str:
        lower_message = message.lower()
        
        if 'policy' in lower_message or 'rule' in lower_message:
            return """📋 **School Policies & Rules**

**Academic Policies:**
- Minimum 75% attendance required for academic progression
- Late assignments accepted with 10% penalty per day
- Make-up tests available for excused absences only

**Behavioral Guidelines:**
- Respect for teachers, staff, and fellow students
- No mobile phones during class hours
- Proper school uniform required daily

**Safety Protocols:**
- Visitor registration required at main office
- Emergency contact information must be current
- Students must remain on campus during school hours

**Communication:**
- Parent-teacher conferences scheduled quarterly
- Progress reports sent home monthly
- Emergency notifications via registered contact methods

For detailed policy information, please refer to the student handbook or contact the school office."""
        
        if 'fee' in lower_message or 'payment' in lower_message:
            return """💰 **Fee Information**

**Tuition Structure:**
- Monthly tuition fees due by 5th of each month
- Late payment penalty of 2% after 10th of month
- Annual fees payable at beginning of academic year

**Payment Methods:**
- Online payment portal available 24/7
- Bank transfer to school account
- Cash payments accepted at school office

**Financial Assistance:**
- Scholarship programs available for merit students
- Fee concessions for economically disadvantaged families
- Installment payment plans upon request

**Contact Financial Office:**
- Office Hours: Monday-Friday, 9:00 AM - 3:00 PM
- Phone: Contact main office for financial department
- Email: Available through school office

For specific fee queries or payment issues, please contact the financial office directly."""
        
        if 'event' in lower_message or 'program' in lower_message:
            return """🎉 **School Events & Programs**

**Upcoming Events:**
- Annual Sports Day: Coming in next quarter
- Science Fair: Student project submissions open
- Cultural Program: Talent show registrations available
- Parent-Teacher Meeting: Scheduled monthly

**Regular Programs:**
- Library reading sessions every Tuesday
- Computer lab access during lunch hours
- Art and craft workshops on Fridays
- Music lessons available after school

**Special Programs:**
- Summer camp registration opens in April
- Educational field trips planned quarterly
- Guest speaker sessions monthly
- Career guidance workshops for senior students

**Participation:**
- Students encouraged to participate in all events
- Parent volunteers welcome for event organization
- Registration typically required in advance

For event schedules and registration, please contact the activities coordinator through the school office."""
        
        return """ℹ️ **General School Information**

**School Hours:**
- Classes: 8:00 AM - 3:00 PM
- Office: 7:30 AM - 4:00 PM
- Library: 8:00 AM - 5:00 PM

**Contact Information:**
- Main Office: Available during office hours
- Emergency Contact: 24/7 emergency line available
- Website: Check school website for updates

**Facilities:**
- Well-equipped science laboratories
- Modern computer lab with internet access
- Comprehensive library with study areas
- Sports facilities including playground and gym

**Services:**
- School transportation available
- Cafeteria serving healthy meals
- Medical room with qualified nurse
- Counseling services for students

**Quick Help:**
- For attendance issues: Contact class teacher
- For grade concerns: Speak with subject teacher
- For general queries: Visit school office
- For emergencies: Use emergency contact number

What specific information would you like to know more about?"""
    
    def _generate_help_response(self) -> str:
        return """🤖 **How I Can Help You**

I'm SchoolBot, your assistant for accessing your child's school information. Here's what I can do:

**Student Information:**
- "Show me attendance for this month"
- "What are the latest test scores?"
- "How is my child performing in math?"

**Schedules & Timetables:**
- "What's the class schedule for today?"
- "When are the upcoming exams?"
- "What time does math class start?"

**Teacher Information:**
- "Who is the math teacher?"
- "How can I contact the science teacher?"
- "What subjects does Mrs. Smith teach?"

**School Information:**
- "What is the school's attendance policy?"
- "When are the school fees due?"
- "What events are coming up?"

**Tips for Better Results:**
- Be specific about what information you need
- Mention subject names when asking about grades
- Ask about specific time periods for attendance

**Privacy & Security:**
- I only share information about your registered child
- All conversations are secure and confidential
- Your data is protected according to school privacy policies

What would you like to know about your child's education?"""
    
    def _generate_greeting(self, context: Dict[str, Any]) -> str:
        return """👋 **Hello! Welcome back to SchoolBot**

I'm here to help you stay informed about your child's academic progress and school activities.

**Quick Access:**
- 📊 Check attendance records
- 📚 View latest grades and test scores
- 📅 Get class schedules and timetables
- 👨‍🏫 Find teacher contact information
- ℹ️ Access school policies and information

**What would you like to know today?**
Just ask me about attendance, grades, schedules, or any school-related questions!

Example: "Show me this week's attendance" or "What are the latest math scores?\""""
    
    def _is_greeting(self, message: str) -> bool:
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'start', 'begin']
        return any(greeting in message for greeting in greetings)
    
    def _is_attendance_query(self, message: str) -> bool:
        return any(word in message for word in ['attendance', 'absent', 'present', 'late'])
    
    def _is_grade_query(self, message: str) -> bool:
        return any(word in message for word in ['grade', 'score', 'mark', 'test', 'exam', 'performance'])
    
    def _is_schedule_query(self, message: str) -> bool:
        return any(word in message for word in ['schedule', 'timetable', 'class', 'time', 'when'])
    
    def _is_teacher_query(self, message: str) -> bool:
        return any(word in message for word in ['teacher', 'instructor', 'contact', 'email'])
    
    def _is_general_school_query(self, message: str) -> bool:
        return any(word in message for word in ['policy', 'rule', 'fee', 'event', 'program', 'school'])