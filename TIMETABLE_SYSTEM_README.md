# Enhanced Timetable Generation System

## Overview

The timetable generation system has been completely rewritten to address the following requirements:

1. **Unique timetables per batch/class** - Each batch gets its own unique timetable
2. **No teacher conflicts** - One teacher can only be in one class at a time
3. **Proper session limits** - Maximum 5 sessions per week per subject
4. **Daily session limits** - Maximum 1-2 sessions per day per subject
5. **Morning/Afternoon separation** - Subjects are separated between morning and afternoon sessions
6. **Lab scheduling** - Labs are scheduled as 3 continuous periods
7. **First period priority** - First periods of morning and afternoon sessions prioritize subjects

## Key Features

### 1. Session Management
- **Weekly Limit**: Each subject has a maximum of 5 sessions per week
- **Daily Limit**: Each subject has a maximum of 2 sessions per day
- **Half-Day Separation**: Only 1 session per subject per half-day (morning/afternoon)

### 2. Teacher Conflict Resolution
- **Global Teacher Tracking**: Teachers are tracked across all batches to prevent conflicts
- **Real-time Availability**: System checks teacher availability before scheduling
- **Cross-batch Validation**: Prevents same teacher being scheduled in multiple batches simultaneously

### 3. Lab Session Handling
- **Continuous Scheduling**: Labs are scheduled as 3 continuous periods
- **Proper Room Assignment**: Labs are assigned to lab rooms when available
- **Half-day Placement**: Labs are placed in either morning (periods 2-4) or afternoon (periods 6-8)

### 4. Morning/Afternoon Sessions
- **Morning Sessions**: Periods 1-4
- **Afternoon Sessions**: Periods 5-8
- **First Period Priority**: Periods 1 and 5 are prioritized for regular subjects

## Database Schema Changes

### New Fields Added:

#### Teachers Table
- `max_sessions_per_week`: Maximum sessions a teacher can handle per week (default: 10)

#### Subjects Table
- `max_sessions_per_day`: Maximum sessions per day for this subject (default: 2)
- `lab_duration`: Duration in periods for lab subjects (default: 3)
- `sessions_per_week`: Updated default from 3 to 5

#### Subject Offerings Table
- `max_sessions_per_day`: Maximum sessions per day for this offering (default: 2)
- `priority`: Priority for scheduling (higher number = higher priority)
- `sessions_per_week`: Updated default from 3 to 5

#### Timetable Entries Table
- `is_lab_session`: Boolean flag indicating if this is a lab session
- `lab_session_part`: Part number of the lab session (1, 2, or 3)

## Usage

### 1. Database Migration
First, run the migration script to update your database:

```bash
cd backend
python migrate_db.py
```

### 2. Creating Subject Offerings
When creating subject offerings, you can now specify:
- `sessions_per_week`: How many sessions per week (max 5)
- `max_sessions_per_day`: How many sessions per day (max 2)
- `priority`: Scheduling priority (higher = more important)

### 3. Generating Timetables
The timetable generation process now follows this order:
1. **First Period Scheduling**: Ensures periods 1 and 5 have subjects
2. **Lab Scheduling**: Places labs as 3 continuous periods
3. **Regular Subject Filling**: Fills remaining slots with regular subjects

### 4. API Endpoints

#### Generate Timetable
```http
POST /timetables/generate?batch_id=1
```

#### Get Timetable
```http
GET /timetables/{timetable_id}
```

Response includes:
- Subject name, teacher name, room name
- Half-day indicator (AM/PM)
- Lab session information

## Constraints and Rules

### 1. Subject Scheduling Rules
- Maximum 5 sessions per week per subject
- Maximum 2 sessions per day per subject
- Maximum 1 session per half-day per subject
- Regular subjects cannot be labs

### 2. Lab Scheduling Rules
- Labs must be 3 continuous periods
- Labs can start at period 2 (morning) or period 6 (afternoon)
- Labs use lab rooms when available
- Lab sessions are marked with `is_lab_session=True`

### 3. Teacher Availability Rules
- One teacher can only be in one place at a time
- Teacher availability is checked across all batches
- Teachers have a maximum sessions per day limit
- Teachers have a maximum sessions per week limit

### 4. Room Assignment Rules
- Lab subjects get lab rooms when available
- Regular subjects get classroom rooms
- Room assignment is consistent for each subject

## Example Timetable Structure

```
Day: Monday
Period 1 (AM): Mathematics - Teacher A - Room 101
Period 2 (AM): Physics Lab (Part 1) - Teacher B - Lab 1
Period 3 (AM): Physics Lab (Part 2) - Teacher B - Lab 1
Period 4 (AM): Physics Lab (Part 3) - Teacher B - Lab 1
Period 5 (PM): English - Teacher C - Room 102
Period 6 (PM): Chemistry - Teacher D - Room 103
Period 7 (PM): [Empty]
Period 8 (PM): Computer Science - Teacher E - Room 104
```

## Benefits

1. **No Conflicts**: Teachers cannot be double-booked
2. **Balanced Distribution**: Subjects are evenly distributed across the week
3. **Proper Lab Handling**: Labs get the continuous time they need
4. **Flexible Constraints**: Easy to modify session limits and priorities
5. **Unique Timetables**: Each batch gets a unique, optimized timetable
6. **Morning/Afternoon Balance**: Subjects are properly distributed across half-days

## Troubleshooting

### Common Issues:

1. **Teacher Conflicts**: Check if teacher is already assigned to another batch
2. **Lab Scheduling Failures**: Ensure lab rooms are available and properly marked
3. **Subject Over-scheduling**: Verify session limits are set correctly
4. **Empty Periods**: May occur if constraints are too restrictive

### Solutions:

1. **Increase Teacher Pool**: Add more teachers to reduce conflicts
2. **Adjust Session Limits**: Modify `sessions_per_week` and `max_sessions_per_day`
3. **Set Priorities**: Use the `priority` field to ensure important subjects get scheduled first
4. **Check Room Types**: Ensure rooms are properly categorized as "LAB" or "CLASSROOM"

## Future Enhancements

1. **Teacher Preferences**: Allow teachers to specify preferred time slots
2. **Subject Dependencies**: Handle prerequisite relationships between subjects
3. **Room Capacity Matching**: Match room capacity with batch size
4. **Conflict Resolution UI**: Provide interface for resolving scheduling conflicts
5. **Automated Optimization**: Use genetic algorithms for better optimization
