-- Smart Class Scheduler Database Schema
-- Create database
CREATE DATABASE IF NOT EXISTS smart_class_scheduler;
USE smart_class_scheduler;

-- Users table for authentication
CREATE TABLE Users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'faculty', 'student') NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Classrooms table
CREATE TABLE Classrooms (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    capacity INT NOT NULL,
    building VARCHAR(50),
    floor INT,
    has_projector BOOLEAN DEFAULT FALSE,
    has_computer BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Faculty table
CREATE TABLE Faculty (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    max_hours_per_day INT DEFAULT 8,
    max_hours_per_week INT DEFAULT 40,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subjects table
CREATE TABLE Subjects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    credit_hours INT NOT NULL,
    semester INT NOT NULL,
    year INT NOT NULL,
    is_lab BOOLEAN DEFAULT FALSE,
    requires_special_equipment BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Constraints table
CREATE TABLE Constraints (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    type ENUM('faculty_availability', 'room_availability', 'subject_conflict', 'time_preference', 'capacity') NOT NULL,
    description TEXT,
    priority ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Timetables table
CREATE TABLE Timetables (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    semester ENUM('fall', 'spring', 'summer') NOT NULL,
    status ENUM('draft', 'approved', 'locked') DEFAULT 'draft',
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP NULL,
    locked_at TIMESTAMP NULL,
    FOREIGN KEY (created_by) REFERENCES Users(id)
);

-- Schedule entries table
CREATE TABLE ScheduleEntries (
    id INT PRIMARY KEY AUTO_INCREMENT,
    timetable_id INT NOT NULL,
    subject_id INT NOT NULL,
    faculty_id INT NOT NULL,
    classroom_id INT NOT NULL,
    day_of_week ENUM('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (timetable_id) REFERENCES Timetables(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES Subjects(id),
    FOREIGN KEY (faculty_id) REFERENCES Faculty(id),
    FOREIGN KEY (classroom_id) REFERENCES Classrooms(id)
);

-- Faculty subject assignments
CREATE TABLE FacultySubjectAssignments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    faculty_id INT NOT NULL,
    subject_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (faculty_id) REFERENCES Faculty(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES Subjects(id) ON DELETE CASCADE,
    UNIQUE KEY unique_faculty_subject (faculty_id, subject_id)
);

-- Faculty availability constraints
CREATE TABLE FacultyAvailability (
    id INT PRIMARY KEY AUTO_INCREMENT,
    faculty_id INT NOT NULL,
    day_of_week ENUM('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (faculty_id) REFERENCES Faculty(id) ON DELETE CASCADE
);

-- Room availability constraints
CREATE TABLE RoomAvailability (
    id INT PRIMARY KEY AUTO_INCREMENT,
    classroom_id INT NOT NULL,
    day_of_week ENUM('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday') NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (classroom_id) REFERENCES Classrooms(id) ON DELETE CASCADE
);

-- Indexes for better performance
CREATE INDEX idx_schedule_entries_timetable ON ScheduleEntries(timetable_id);
CREATE INDEX idx_schedule_entries_faculty ON ScheduleEntries(faculty_id);
CREATE INDEX idx_schedule_entries_classroom ON ScheduleEntries(classroom_id);
CREATE INDEX idx_schedule_entries_time ON ScheduleEntries(day_of_week, start_time);
CREATE INDEX idx_timetables_status ON Timetables(status);
CREATE INDEX idx_users_role ON Users(role);
