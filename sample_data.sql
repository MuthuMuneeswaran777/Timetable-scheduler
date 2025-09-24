-- Sample data for Smart Class Scheduler
USE smart_class_scheduler;

-- Sample Users (password is 'password123' hashed with bcrypt)
INSERT INTO Users (username, email, password_hash, role, full_name) VALUES
('admin1', 'admin@university.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/L3cJ1X6R7T8v.Zq', 'admin', 'Dr. Sarah Johnson'),
('faculty1', 'prof.smith@university.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/L3cJ1X6R7T8v.Zq', 'faculty', 'Prof. John Smith'),
('faculty2', 'dr.brown@university.edu', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/L3cJ1X6R7T8v.Zq', 'faculty', 'Dr. Emily Brown');

-- Sample Classrooms
INSERT INTO Classrooms (name, capacity, building, floor, has_projector, has_computer) VALUES
('Room 101', 30, 'Main Building', 1, TRUE, TRUE),
('Room 102', 25, 'Main Building', 1, FALSE, FALSE),
('Room 201', 40, 'Science Building', 2, TRUE, TRUE),
('Room 202', 35, 'Science Building', 2, FALSE, TRUE),
('Lab 301', 20, 'Lab Building', 3, TRUE, TRUE),
('Lab 302', 15, 'Lab Building', 3, TRUE, TRUE);

-- Sample Faculty
INSERT INTO Faculty (name, email, department, phone, max_hours_per_day, max_hours_per_week) VALUES
('Prof. John Smith', 'prof.smith@university.edu', 'Computer Science', '+1234567890', 8, 40),
('Dr. Emily Brown', 'dr.brown@university.edu', 'Mathematics', '+1234567891', 6, 30),
('Dr. Michael Davis', 'dr.davis@university.edu', 'Physics', '+1234567892', 8, 35),
('Prof. Lisa Wilson', 'prof.wilson@university.edu', 'Chemistry', '+1234567893', 7, 35);

-- Sample Subjects
INSERT INTO Subjects (code, name, department, credit_hours, semester, year, is_lab, requires_special_equipment) VALUES
('CS101', 'Introduction to Programming', 'Computer Science', 3, 1, 2024, FALSE, FALSE),
('CS201', 'Data Structures', 'Computer Science', 4, 3, 2024, TRUE, TRUE),
('MATH101', 'Calculus I', 'Mathematics', 4, 1, 2024, FALSE, FALSE),
('MATH201', 'Linear Algebra', 'Mathematics', 3, 3, 2024, FALSE, FALSE),
('PHYS101', 'General Physics I', 'Physics', 4, 1, 2024, TRUE, TRUE),
('CHEM101', 'General Chemistry', 'Chemistry', 4, 1, 2024, TRUE, TRUE);

-- Faculty Subject Assignments
INSERT INTO FacultySubjectAssignments (faculty_id, subject_id) VALUES
(1, 1), -- Prof. Smith teaches CS101
(1, 2), -- Prof. Smith teaches CS201
(2, 3), -- Dr. Brown teaches MATH101
(2, 4), -- Dr. Brown teaches MATH201
(3, 5), -- Dr. Davis teaches PHYS101
(4, 6); -- Prof. Wilson teaches CHEM101

-- Faculty Availability (sample - Monday to Friday, 9 AM to 5 PM)
INSERT INTO FacultyAvailability (faculty_id, day_of_week, start_time, end_time, is_available) VALUES
(1, 'monday', '09:00:00', '17:00:00', TRUE),
(1, 'tuesday', '09:00:00', '17:00:00', TRUE),
(1, 'wednesday', '09:00:00', '17:00:00', TRUE),
(1, 'thursday', '09:00:00', '17:00:00', TRUE),
(1, 'friday', '09:00:00', '17:00:00', TRUE),
(2, 'monday', '10:00:00', '16:00:00', TRUE),
(2, 'tuesday', '10:00:00', '16:00:00', TRUE),
(2, 'wednesday', '10:00:00', '16:00:00', TRUE),
(2, 'thursday', '10:00:00', '16:00:00', TRUE),
(2, 'friday', '10:00:00', '16:00:00', TRUE);

-- Room Availability (all rooms available Monday to Friday, 8 AM to 6 PM)
INSERT INTO RoomAvailability (classroom_id, day_of_week, start_time, end_time, is_available) VALUES
(1, 'monday', '08:00:00', '18:00:00', TRUE),
(1, 'tuesday', '08:00:00', '18:00:00', TRUE),
(1, 'wednesday', '08:00:00', '18:00:00', TRUE),
(1, 'thursday', '08:00:00', '18:00:00', TRUE),
(1, 'friday', '08:00:00', '18:00:00', TRUE),
(2, 'monday', '08:00:00', '18:00:00', TRUE),
(2, 'tuesday', '08:00:00', '18:00:00', TRUE),
(2, 'wednesday', '08:00:00', '18:00:00', TRUE),
(2, 'thursday', '08:00:00', '18:00:00', TRUE),
(2, 'friday', '08:00:00', '18:00:00', TRUE),
(3, 'monday', '08:00:00', '18:00:00', TRUE),
(3, 'tuesday', '08:00:00', '18:00:00', TRUE),
(3, 'wednesday', '08:00:00', '18:00:00', TRUE),
(3, 'thursday', '08:00:00', '18:00:00', TRUE),
(3, 'friday', '08:00:00', '18:00:00', TRUE);

-- Sample Timetable
INSERT INTO Timetables (name, academic_year, semester, status, created_by) VALUES
('Fall 2024 Draft', '2024-2025', 'fall', 'draft', 1);

-- Sample Schedule Entries (basic schedule for testing)
INSERT INTO ScheduleEntries (timetable_id, subject_id, faculty_id, classroom_id, day_of_week, start_time, end_time) VALUES
(1, 1, 1, 1, 'monday', '09:00:00', '10:30:00'), -- CS101 in Room 101
(1, 3, 2, 2, 'monday', '14:00:00', '16:00:00'), -- MATH101 in Room 102
(1, 5, 3, 3, 'tuesday', '10:00:00', '12:00:00'), -- PHYS101 in Room 201
(1, 6, 4, 5, 'wednesday', '13:00:00', '15:00:00'); -- CHEM101 in Lab 301
