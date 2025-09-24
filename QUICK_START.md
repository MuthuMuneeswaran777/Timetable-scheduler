# 🚀 QUICK START GUIDE

## 🎯 IMMEDIATE ACTIONS

### 1. Start the System
```bash
.\start_clean.bat
```

### 2. Open Browser
```
http://localhost:3000
```

### 3. Login Credentials
- **Username:** `admin1`
- **Password:** `password123`
- **Role:** Administrator

## 🔑 AVAILABLE USERS

| Username | Password | Role | Access Level |
|----------|----------|------|--------------|
| admin1 | password123 | Admin | Full Access |
| faculty1 | password123 | Faculty | Teacher Access |
| student1 | password123 | Student | View Only |

## 🎮 MAIN FEATURES

### Admin Dashboard
- ✅ User Management
- ✅ Department Setup
- ✅ Teacher Management
- ✅ Timetable Generation
- ✅ System Settings

### Faculty Portal
- ✅ View Schedules
- ✅ Check Assignments
- ✅ Update Profile

### Student Portal
- ✅ View Timetables
- ✅ Check Classes
- ✅ Academic Information

## 🔧 SYSTEM ARCHITECTURE

```
Frontend (React)
    ↓
Backend API (FastAPI)
    ↓
Data Storage (JSON)
    ↓
Authentication (JWT)
```

## 📱 API ENDPOINTS

- `POST /token` - Login
- `GET /users/me` - Current user
- `GET /departments/` - Department data
- `GET /teachers/` - Teacher data
- `POST /timetable/generate` - Generate schedules
- `GET /timetable/view` - View timetables

## 🚨 TROUBLESHOOTING

### If Login Fails:
1. Check credentials (admin1/password123)
2. Verify backend is running on port 8001
3. Check browser console for errors

### If No Data Appears:
1. Wait for data to load
2. Check if JSON files exist
3. Verify file permissions

### If Server Won't Start:
1. Check Python environment
2. Verify dependencies
3. Check for port conflicts

## 🎉 SUCCESS METRICS

- ✅ Authentication: WORKING
- ✅ Data Persistence: ACTIVE
- ✅ Timetable System: READY
- ✅ User Management: COMPLETE
- ✅ API Services: OPERATIONAL

**Your Smart Class Scheduler is ready for use!** 🎊
