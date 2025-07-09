# SchoolBot - School Parent-Interface Chatbot System

A secure, intelligent chatbot system designed to facilitate communication between parents and schools, providing access to student information, grades, attendance, and schedules.

## Features

### 🔐 **Security & Authentication**
- JWT-based authentication for parents
- Password hashing with bcrypt
- Rate limiting to prevent abuse
- Session management for chat conversations
- Data privacy compliance for student information

### 🤖 **Intelligent Chatbot**
- Natural language processing for parent queries
- Context-aware conversations
- Structured responses with formatting
- Multi-topic support (attendance, grades, schedules, etc.)
- Help system with usage examples

### 📊 **Student Information Access**
- **Attendance Records**: Monthly statistics, absence tracking
- **Academic Performance**: Grades, test scores, subject-wise performance
- **Class Schedules**: Timetables, teacher assignments, room information
- **Teacher Information**: Contact details, subject mappings

### 💻 **User Interface**
- Responsive web interface
- Real-time chat functionality
- Mobile-friendly design
- Typing indicators and message formatting
- Secure login/logout system

## Technology Stack

- **Backend**: Python FastAPI
- **Database**: SQLite with secure schema design
- **Authentication**: JWT tokens with python-jose
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Security**: bcrypt via passlib, SlowAPI rate limiting, CORS protection

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip package manager

### 1. Clone and Install Dependencies
```bash
git clone https://github.com/chethanmp6/schoolprincipal.git
cd schoolprincipal
pip install -r requirements.txt
```

### 2. Environment Setup
```bash
# Create .env file with your configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=sqlite:///data/school.db
```

### 3. Initialize Database and Sample Data
```bash
python scripts/seed_data.py
```

### 4. Run the Application
```bash
python main.py
```

The application will be available at `http://localhost:8000`

**FastAPI Features:**
- **Interactive API Documentation**: Available at `http://localhost:8000/docs`
- **ReDoc Documentation**: Available at `http://localhost:8000/redoc`
- **High Performance**: Async support and automatic validation
- **Type Safety**: Pydantic models for request/response validation

## Sample Login Credentials

After running the seed script, you can use these credentials:

- **Email**: john.johnson@email.com, **Password**: password123 (Student ID: 12345)
- **Email**: mary.wilson@email.com, **Password**: password123 (Student ID: 12346)
- **Email**: james.davis@email.com, **Password**: password123 (Student ID: 12347)
- **Email**: linda.brown@email.com, **Password**: password123 (Student ID: 12348)
- **Email**: carlos.garcia@email.com, **Password**: password123 (Student ID: 12349)

## Usage Examples

### Authentication Flow
1. Parents log in with their registered email and password
2. System creates a secure chat session
3. Parents provide student ID for verification
4. Chatbot provides personalized responses

### Sample Queries
- **Attendance**: "Show me attendance for this month"
- **Grades**: "What are the latest test scores?"
- **Schedule**: "What's the class schedule for today?"
- **Teachers**: "Who is the math teacher?"
- **School Info**: "What is the school's fee policy?"

## API Endpoints

### Authentication
- `POST /api/auth/login` - Parent login
- `POST /api/chat/session` - Create chat session

### Student Information
- `GET /api/student/info` - Get student details
- `GET /api/student/attendance` - Get attendance records
- `GET /api/student/grades` - Get academic performance
- `GET /api/student/schedule` - Get class schedule

### Chat System
- `POST /api/chat/message` - Send message to chatbot

## Security Features

### Data Protection
- Password hashing with bcrypt
- JWT token-based authentication
- Rate limiting (5 login attempts per minute)
- Session-based chat management
- Input validation and sanitization

### Privacy Compliance
- Parents can only access their own child's data
- Student ID verification required
- Secure data storage and transmission
- Audit trail for all data access

### Error Handling
- Graceful error responses
- Logging for security events
- Protection against common attacks
- Safe failure modes

## Database Schema

### Core Tables
- **students**: Student information and parent associations
- **teachers**: Teacher details and subject assignments
- **attendance**: Daily attendance records
- **grades**: Test scores and academic performance
- **class_schedule**: Timetables and room assignments
- **parent_auth**: Authentication and authorization
- **chat_sessions**: Conversation history and context

## Chatbot Capabilities

### Query Types Supported
1. **Attendance Queries**: Monthly statistics, absence tracking
2. **Academic Performance**: Grades, averages, subject-wise performance
3. **Schedule Information**: Class timetables, exam schedules
4. **Teacher Information**: Contact details, subject mappings
5. **School Policies**: Rules, fees, events, general information

### Response Format
- Structured markdown formatting
- Emoji indicators for better readability
- Tabular data for schedules and grades
- Contextual help and suggestions
- Error handling with helpful messages

## Development

### Project Structure
```
SchoolPrincipal/
├── main.py                # Main FastAPI application
├── models/
│   ├── database.py        # Database models and operations
│   ├── schemas.py         # Pydantic models for validation
│   └── __init__.py
├── auth/
│   ├── auth.py            # Authentication utilities
│   └── __init__.py
├── chatbot/
│   ├── school_bot.py      # Chatbot logic and NLP
│   └── __init__.py
├── templates/
│   └── index.html         # Web interface
├── scripts/
│   ├── seed_data.py       # Database seeding
│   └── __init__.py
├── data/                  # SQLite database storage
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
└── README.md
```

### Testing
```bash
# Run the application in development mode
python main.py

# Test API endpoints
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "john.johnson@email.com", "password": "password123"}'

# Access interactive API documentation
# Open http://localhost:8000/docs in your browser

# Run tests
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For support and questions:
- Check the documentation above
- Review the code comments
- Create an issue in the repository
- Contact the development team

---

**Note**: This is a defensive security system designed to protect student data. All security measures should be regularly reviewed and updated according to current best practices.
