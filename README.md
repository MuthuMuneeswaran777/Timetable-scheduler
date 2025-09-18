# Enhanced Timetable Generation System

An intelligent timetable generation system with advanced conflict resolution for educational institutions.

## 🌟 Features

### Core Functionality
- **Unique Timetables**: Each batch/class gets its own unique timetable
- **No Teacher Conflicts**: One teacher can only be in one class at a time
- **Smart Session Management**: Maximum 5 sessions per week, 2 per day per subject
- **Morning/Afternoon Separation**: Subjects are properly distributed across half-days
- **Lab Scheduling**: Labs are scheduled as 3 continuous periods with intelligent conflict resolution

### Advanced Lab Conflict Resolution
- **Automatic Conflict Detection**: Detects when lab teachers are assigned to multiple batches
- **Intelligent Rescheduling**: Automatically reschedules conflicted labs to alternative time slots
- **Priority-Based Scheduling**: Morning slots preferred, then afternoon, then next day
- **Comprehensive Logging**: Detailed feedback on scheduling decisions and conflicts

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with SQLAlchemy ORM
- **Database**: SQLite (default) or MySQL
- **API Documentation**: Auto-generated Swagger UI
- **Enhanced Scheduler**: Intelligent timetable generation with conflict resolution

### Frontend (React + Vite)
- **Framework**: React with Vite build tool
- **Styling**: Tailwind CSS
- **Development**: Hot reload and fast refresh

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd SIH
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

3. **Database Migration**
   ```bash
   cd ..
   backend\.venv\Scripts\python -m backend.migrate_db
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

1. **Start Backend** (Terminal 1)
   ```bash
   # From project root
   backend\.venv\Scripts\uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Frontend** (Terminal 2)
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📊 API Endpoints

### Data Management
- `GET /data/teachers` - List all teachers
- `POST /data/teachers` - Create new teacher
- `GET /data/subjects` - List all subjects
- `POST /data/subjects` - Create new subject
- `GET /data/batches` - List all batches
- `POST /data/batches` - Create new batch
- `GET /data/rooms` - List all rooms
- `POST /data/rooms` - Create new room
- `GET /data/subject_offerings` - List subject offerings
- `POST /data/subject_offerings` - Create subject offering

### Timetable Generation
- `POST /timetables/generate?batch_id={id}` - Generate timetable for batch
- `GET /timetables/{id}` - View generated timetable
- `GET /timetables` - List all timetables

## 🧪 Testing

Run the lab conflict resolution test:
```bash
backend\.venv\Scripts\python -m backend.test_lab_conflicts
```

## 📁 Project Structure

```
SIH/
├── backend/
│   ├── models/
│   │   └── models.py          # Database models
│   ├── routers/
│   │   ├── data.py           # Data management endpoints
│   │   └── timetables.py     # Timetable endpoints
│   ├── scheduler.py          # Enhanced timetable scheduler
│   ├── database.py           # Database configuration
│   ├── main.py              # FastAPI application
│   ├── migrate_db.py        # Database migration script
│   ├── test_lab_conflicts.py # Lab conflict resolution test
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/                 # React source code
│   ├── public/              # Static assets
│   ├── package.json         # Node.js dependencies
│   └── vite.config.js       # Vite configuration
├── TIMETABLE_SYSTEM_README.md # Detailed system documentation
└── README.md               # This file
```

## 🔧 Configuration

### Database Configuration
- **Default**: SQLite at `backend/dev.db`
- **MySQL**: Set `DATABASE_URL` environment variable
  ```bash
  DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/sih
  ```

### Environment Variables
- `DATABASE_URL`: Database connection string
- `CORS_ORIGINS`: Allowed CORS origins (default: "*")

## 📋 Constraints and Rules

### Subject Scheduling
- Maximum 5 sessions per week per subject
- Maximum 2 sessions per day per subject
- Maximum 1 session per half-day per subject
- First periods (1 and 5) prioritized for subjects

### Lab Scheduling
- Labs must be 3 continuous periods
- Labs can start at period 2 (morning) or period 6 (afternoon)
- Automatic conflict resolution for shared lab teachers
- Labs use lab rooms when available

### Teacher Management
- One teacher can only be in one place at a time
- Teacher availability checked across all batches
- Automatic rescheduling when conflicts detected

## 🎯 Key Achievements

✅ **Unique Timetables**: Each batch gets its own optimized timetable  
✅ **Zero Teacher Conflicts**: Comprehensive conflict detection and resolution  
✅ **Smart Lab Scheduling**: Automatic rescheduling of conflicted lab sessions  
✅ **Constraint Compliance**: All scheduling rules properly enforced  
✅ **Scalable Architecture**: Supports multiple batches and complex scheduling scenarios  

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the API documentation at http://localhost:8000/docs
- Review the detailed system documentation in `TIMETABLE_SYSTEM_README.md`
- Run the test suite to verify functionality

---

**Built with ❤️ for Smart India Hackathon**
