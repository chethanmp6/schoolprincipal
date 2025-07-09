from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import logging
from models.database import Database
from chatbot.school_bot import SchoolBot
import uuid

load_dotenv()

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-this')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)

CORS(app)
jwt = JWTManager(app)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = Database()
school_bot = SchoolBot()

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = db.authenticate_parent(email, password)
        
        if user:
            access_token = create_access_token(
                identity=email,
                additional_claims={'student_ids': user['student_ids']}
            )
            return jsonify({
                'access_token': access_token,
                'student_ids': user['student_ids'].split(','),
                'message': 'Login successful'
            }), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/chat/session', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def create_chat_session():
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        student_id = data.get('student_id')
        
        if not student_id:
            return jsonify({'error': 'Student ID is required'}), 400
        
        session_id = str(uuid.uuid4())
        
        db.create_chat_session(session_id, current_user, student_id)
        
        return jsonify({
            'session_id': session_id,
            'message': 'Chat session created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Create session error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/chat/message', methods=['POST'])
@jwt_required()
@limiter.limit("30 per minute")
def send_message():
    try:
        current_user = get_jwt_identity()
        data = request.get_json()
        session_id = data.get('session_id')
        message = data.get('message')
        
        if not session_id or not message:
            return jsonify({'error': 'Session ID and message are required'}), 400
        
        response = school_bot.process_message(session_id, current_user, message)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Send message error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/student/info', methods=['GET'])
@jwt_required()
def get_student_info():
    try:
        current_user = get_jwt_identity()
        student_id = request.args.get('student_id')
        
        if not student_id:
            return jsonify({'error': 'Student ID is required'}), 400
        
        student = db.get_student_by_parent(current_user, student_id)
        
        if not student:
            return jsonify({'error': 'Student not found or access denied'}), 404
        
        return jsonify({
            'student_id': student['student_id'],
            'name': student['name'],
            'class': student['class'],
            'section': student['section']
        }), 200
        
    except Exception as e:
        logger.error(f"Get student info error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/student/attendance', methods=['GET'])
@jwt_required()
def get_attendance():
    try:
        current_user = get_jwt_identity()
        student_id = request.args.get('student_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not student_id:
            return jsonify({'error': 'Student ID is required'}), 400
        
        if not start_date or not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        student = db.get_student_by_parent(current_user, student_id)
        if not student:
            return jsonify({'error': 'Student not found or access denied'}), 404
        
        attendance = db.get_attendance(student_id, start_date, end_date)
        
        return jsonify({
            'attendance': attendance,
            'summary': {
                'total_days': len(attendance),
                'present': len([a for a in attendance if a['status'] == 'present']),
                'absent': len([a for a in attendance if a['status'] == 'absent']),
                'late': len([a for a in attendance if a['status'] == 'late'])
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get attendance error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/student/grades', methods=['GET'])
@jwt_required()
def get_grades():
    try:
        current_user = get_jwt_identity()
        student_id = request.args.get('student_id')
        subject = request.args.get('subject')
        
        if not student_id:
            return jsonify({'error': 'Student ID is required'}), 400
        
        student = db.get_student_by_parent(current_user, student_id)
        if not student:
            return jsonify({'error': 'Student not found or access denied'}), 404
        
        grades = db.get_grades(student_id, subject)
        
        return jsonify({'grades': grades}), 200
        
    except Exception as e:
        logger.error(f"Get grades error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/student/schedule', methods=['GET'])
@jwt_required()
def get_schedule():
    try:
        current_user = get_jwt_identity()
        student_id = request.args.get('student_id')
        
        if not student_id:
            return jsonify({'error': 'Student ID is required'}), 400
        
        student = db.get_student_by_parent(current_user, student_id)
        if not student:
            return jsonify({'error': 'Student not found or access denied'}), 404
        
        schedule = db.get_class_schedule(student['class'], student['section'])
        
        return jsonify({'schedule': schedule}), 200
        
    except Exception as e:
        logger.error(f"Get schedule error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    os.makedirs('data', exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)