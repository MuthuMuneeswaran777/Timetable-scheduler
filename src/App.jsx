import React, { useState, useEffect } from 'react';
import './App.css';

// API base URL - Updated for persistent backend
const API_BASE_URL = 'http://localhost:8001';

// Safe rendering helper
const safeRender = (value, fallback = 'N/A') => {
  if (value === null || value === undefined) return fallback;
  if (typeof value === 'object') {
    if (Array.isArray(value)) return value.length > 0 ? value.join(', ') : fallback;
    return value.name || value.toString() || fallback;
  }
  return String(value);
};

function App() {
  const [currentView, setCurrentView] = useState('login');
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [loading, setLoading] = useState(false);
  const [timetableData, setTimetableData] = useState({
    departments: [],
    teachers: [],
    students: [],
    timetable: [],
    selectedDepartment: '',
    selectedYear: '',
    selectedSection: ''
  });
  const [currentUser, setCurrentUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteItem, setDeleteItem] = useState(null);
  const [showDeleteAllConfirm, setShowDeleteAllConfirm] = useState(false);
  const [deleteAllLoading, setDeleteAllLoading] = useState(false);
  const [classrooms, setClassrooms] = useState([]);
  const [faculty, setFaculty] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [timetables, setTimetables] = useState([]);
  const [loginForm, setLoginForm] = useState({
    username: '',
    password: '',
    role: 'admin'
  });
  const [selectedSubjects, setSelectedSubjects] = useState([]);
  const [showChangePassword, setShowChangePassword] = useState(false);
  const [passwordChangeForm, setPasswordChangeForm] = useState({ currentPassword: '', newPassword: '', confirmPassword: '' });
  const [newUserForm, setNewUserForm] = useState({ username: '', email: '', password: '', fullName: '', role: 'faculty' });
  const [newClassroomForm, setNewClassroomForm] = useState({ name: '', capacity: '', building: '', floor: '', hasProjector: false, hasComputer: false });
  const [newFacultyForm, setNewFacultyForm] = useState({ name: '', email: '', department: '', phone: '', maxHoursPerDay: 8, maxHoursPerWeek: 40 });
  const [newSubjectForm, setNewSubjectForm] = useState({ code: '', name: '', department: '', creditHours: '', semester: '', year: '', isLab: false, requiresSpecialEquipment: false });
  const [newTimetableForm, setNewTimetableForm] = useState({ name: '', academicYear: '', semester: 'fall' });
  
  // Timetable creation states
  const [timetableSetup, setTimetableSetup] = useState({
    departments: [],
    teachers: [],
    currentStep: 1,
    totalSteps: 4
  });
  const [currentDepartment, setCurrentDepartment] = useState({
    name: '',
    classes: [],
    labs: [],
    years: 4,
    sections: [],
    year_subjects: {},  // Year-wise subjects instead of flat subjects array
    year_labs: {}  // Year-wise labs (optional)
  });
  const [currentTeacher, setCurrentTeacher] = useState({
    name: '',
    employee_id: '',
    subjects: [],
    department: ''
  });

  // Test backend connectivity
  const testBackendConnection = async () => {
    try {
      console.log('🔍 Testing backend connection...');
      const response = await fetch(`${API_BASE_URL}/health`);
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Backend connection successful:', data);
        return true;
      } else {
        console.error('❌ Backend connection failed:', response.status);
        return false;
      }
    } catch (error) {
      console.error('❌ Backend connection error:', error);
      return false;
    }
  };

  useEffect(() => {
    if (token && currentUser) {
      fetchTimetableData();
    }
  }, [token, currentUser]);

  const fetchCurrentUser = async (authToken) => {
    try {
      const response = await fetch(`${API_BASE_URL}/users/me`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      if (response.ok) {
        const user = await response.json();
        setCurrentUser(user);
        setIsAuthenticated(true);
        fetchData(authToken);
      }
    } catch (error) {
      console.error('Error fetching user:', error);
      logout();
    }
  };

  const fetchData = async (authToken) => {
    try {
      const response = await fetch(`${API_BASE_URL}/timetable/data`, {
        headers: { Authorization: `Bearer ${authToken}` }
      });

      if (response.ok) {
        const data = await response.json();
        setTimetableData(data);
        // Also set individual state variables if they exist
        if (data.classrooms !== undefined) setClassrooms(data.classrooms);
        if (data.faculty !== undefined) setFaculty(data.faculty);
        if (data.subjects !== undefined) setSubjects(data.subjects);
        if (data.timetables !== undefined) setTimetables(data.timetables);
      } else {
        console.error('Failed to fetch data:', response.status);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const login = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('username', loginForm.username);
      formData.append('password', loginForm.password);

      console.log('🔐 Attempting login...');
      console.log(`📡 API URL: ${API_BASE_URL}/token`);
      console.log(`👤 Username: ${loginForm.username}`);

      const response = await fetch(`${API_BASE_URL}/token`, {
        method: 'POST',
        body: formData
      });

      console.log(`📡 Response status: ${response.status}`);
      console.log(`📡 Response headers:`, response.headers);

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Login successful, token received');
        setToken(data.access_token);
        localStorage.setItem('token', data.access_token);
        await fetchCurrentUser(data.access_token);
        console.log('✅ User data fetched successfully');
      } else {
        const errorText = await response.text();
        console.error('❌ Login failed:', response.status, errorText);
        alert(`Invalid credentials (${response.status}): ${errorText}`);
      }
    } catch (error) {
      console.error('❌ Login network error:', error);
      alert(`Login failed: ${error.message}`);
    }
    setLoading(false);
  };

  const logout = () => {
    setIsAuthenticated(false);
    setCurrentUser(null);
    setToken('');
    localStorage.removeItem('token');
    setCurrentView('login');
  };

  const generateSchedule = async () => {
    if (selectedSubjects.length === 0 || !academicYear || !semester) {
      alert('Please select subjects and specify academic year and semester');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/generate-schedule/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          academic_year: academicYear,
          semester: semester,
          subjects: selectedSubjects
        })
      });

      if (response.ok) {
        const options = await response.json();
        setScheduleOptions(options);
        setCurrentView('schedule-options');
      } else {
        alert('Failed to generate schedule');
      }
    } catch (error) {
      console.error('Schedule generation error:', error);
      alert('Schedule generation failed');
    }
    setLoading(false);
  };

  const saveTimetable = async (option) => {
    try {
      const response = await fetch(`${API_BASE_URL}/timetables/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          name: `${option.name} - ${academicYear} ${semester}`,
          academic_year: academicYear,
          semester: semester
        })
      });

      if (response.ok) {
        const timetable = await response.json();
        alert('Timetable saved successfully!');
        fetchData(token);
        setCurrentView('timetables');
      }
    } catch (error) {
      console.error('Save timetable error:', error);
      alert('Failed to save timetable');
    }
  };

  const exportTimetable = async (timetableId, format) => {
    try {
      const response = await fetch(`${API_BASE_URL}/export/timetable/${timetableId}?format=${format}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        const blob = new Blob([data.data], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = data.filename || `timetable_${timetableId}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Export error:', error);
      alert('Export failed');
    }
  };

  const deleteTimetable = async (timetableId) => {
    if (!confirm('Are you sure you want to delete this timetable?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/timetables/${timetableId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        alert('Timetable deleted successfully!');
        fetchData(token);
      } else {
        const error = await response.json();
        alert(`Failed to delete timetable: ${error.detail}`);
      }
    } catch (error) {
      console.error('Delete error:', error);
      alert('Delete failed');
    }
  };

  const deleteClassroom = async (classroomId) => {
    if (!confirm('Are you sure you want to delete this classroom?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/classrooms/${classroomId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        alert('Classroom deleted successfully!');
        fetchData(token);
      } else {
        const error = await response.json();
        alert(`Failed to delete classroom: ${error.detail}`);
      }
    } catch (error) {
      console.error('Delete error:', error);
      alert('Delete failed');
    }
  };

  const deleteFaculty = async (facultyId) => {
    if (!confirm('Are you sure you want to delete this faculty member?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/faculty/${facultyId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        alert('Faculty deleted successfully!');
        fetchData(token);
      } else {
        const error = await response.json();
        alert(`Failed to delete faculty: ${error.detail}`);
      }
    } catch (error) {
      console.error('Delete error:', error);
      alert('Delete failed');
    }
  };

  const deleteSubject = async (subjectId) => {
    if (!confirm('Are you sure you want to delete this subject?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/subjects/${subjectId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        alert('Subject deleted successfully!');
        fetchData(token);
      } else {
        const error = await response.json();
        alert(`Failed to delete subject: ${error.detail}`);
      }
    } catch (error) {
      console.error('Delete error:', error);
      alert('Delete failed');
    }
  };

  const changePassword = async (e) => {
    e.preventDefault();
    
    if (passwordChangeForm.newPassword !== passwordChangeForm.confirmPassword) {
      alert('New passwords do not match');
      return;
    }

    if (passwordChangeForm.newPassword.length < 6) {
      alert('New password must be at least 6 characters long');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/users/change-password`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          current_password: passwordChangeForm.currentPassword,
          new_password: passwordChangeForm.newPassword
        })
      });

      if (response.ok) {
        alert('Password changed successfully!');
        setShowChangePassword(false);
        setPasswordChangeForm({ currentPassword: '', newPassword: '', confirmPassword: '' });
      } else {
        const error = await response.json();
        alert(`Failed to change password: ${error.detail}`);
      }
    } catch (error) {
      console.error('Password change error:', error);
      alert('Password change failed');
    }
    setLoading(false);
  };

  const deleteUser = async (userId) => {
    if (!confirm('Are you sure you want to delete this user?')) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        alert('User deleted successfully!');
        fetchData(token);
      } else {
        const error = await response.json();
        alert(`Failed to delete user: ${error.detail}`);
      }
    } catch (error) {
      console.error('Delete error:', error);
      alert('Delete failed');
    }
  };

  const createUser = async () => {
    if (!newUserForm.username || !newUserForm.email || !newUserForm.password || !newUserForm.fullName) {
      alert('Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/users/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          username: newUserForm.username,
          email: newUserForm.email,
          password: newUserForm.password,
          full_name: newUserForm.fullName,
          role: newUserForm.role
        })
      });

      if (response.ok) {
        alert('User created successfully!');
        setNewUserForm({ username: '', email: '', password: '', fullName: '', role: 'student' });
        fetchData(token);
      } else {
        const error = await response.json();
        alert(`Failed to create user: ${error.detail}`);
      }
    } catch (error) {
      console.error('Create user error:', error);
      alert('Create user failed');
    }
    setLoading(false);
  };

  // Edit and Delete Functions
  const handleEdit = (item, type) => {
    setEditingItem({ ...item, type });
    setEditForm(item);
    setShowEditModal(true);
  };

  const handleDelete = (item, type) => {
    setDeleteItem({ ...item, type });
    setShowDeleteConfirm(true);
  };

  const confirmDelete = async () => {
    setLoading(true);
    try {
      let endpoint = '';
      let identifier = '';

      switch (deleteItem.type) {
        case 'department':
          endpoint = `/departments/${deleteItem.name}`;
          identifier = deleteItem.name;
          break;
        case 'teacher':
          endpoint = `/teachers/${deleteItem.employee_id}`;
          identifier = deleteItem.employee_id;
          break;
        case 'student':
          endpoint = `/students/${deleteItem.roll_number}`;
          identifier = deleteItem.roll_number;
          break;
        default:
          throw new Error('Invalid item type');
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        alert(`${deleteItem.type.charAt(0).toUpperCase() + deleteItem.type.slice(1)} deleted successfully!`);
        fetchData(token);
      } else {
        const error = await response.json();
        alert(`Failed to delete ${deleteItem.type}: ${error.detail}`);
      }
    } catch (error) {
      console.error('Delete error:', error);
      alert('Delete failed');
    }
    setLoading(false);
    setShowDeleteConfirm(false);
    setDeleteItem(null);
  };

  const confirmDeleteAll = async () => {
    setDeleteAllLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/timetable/clear-all`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        const result = await response.json();
        alert(`✅ ${result.message}\n\n📊 Summary:\n• Departments deleted: ${result.reset_summary.departments_deleted}\n• Teachers deleted: ${result.reset_summary.teachers_deleted}\n• Students deleted: ${result.reset_summary.students_deleted}\n• Timetable entries deleted: ${result.reset_summary.timetable_entries_deleted}\n• User credentials deleted: ${result.reset_summary.user_credentials_deleted}`);

        // Refresh data to show empty state
        fetchData(token);

        // Close confirmation dialog
        setShowDeleteAllConfirm(false);
      } else {
        const error = await response.json();
        alert(`❌ Failed to delete all data: ${error.detail}`);
      }
    } catch (error) {
      console.error('Delete all error:', error);
      alert('Failed to delete all data. Please try again.');
    }
    setDeleteAllLoading(false);
  };

  const saveEdit = async () => {
    setLoading(true);
    try {
      let endpoint = '';
      let requestBody = {};

      switch (editingItem.type) {
        case 'department':
          endpoint = `/departments/${editingItem.name}`;
          requestBody = {
            name: editForm.name,
            years: editForm.years,
            sections: editForm.sections,
            classes: editForm.classes,
            labs: editForm.labs,
            year_subjects: editForm.year_subjects
          };
          break;
        case 'teacher':
          endpoint = `/teachers/${editingItem.employee_id}`;
          requestBody = {
            name: editForm.name,
            employee_id: editForm.employee_id,
            department: editForm.department,
            subjects: editForm.subjects
          };
          break;
        case 'student':
          endpoint = `/students/${editingItem.roll_number}`;
          requestBody = {
            name: editForm.name,
            roll_number: editForm.roll_number,
            department: editForm.department,
            year: editForm.year,
            section: editForm.section
          };
          break;
        default:
          throw new Error('Invalid item type');
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(requestBody)
      });

      if (response.ok) {
        alert(`${editingItem.type.charAt(0).toUpperCase() + editingItem.type.slice(1)} updated successfully!`);
        fetchData(token);
      } else {
        const error = await response.json();
        alert(`Failed to update ${editingItem.type}: ${error.detail}`);
      }
    } catch (error) {
      console.error('Update error:', error);
      alert('Update failed');
    }
    setLoading(false);
    setShowEditModal(false);
    setEditingItem(null);
    setEditForm({});
  };

  // Timetable Creation Functions
  const addDepartment = () => {
    if (!currentDepartment.name) {
      alert('Please enter department name');
      return;
    }
    
    setTimetableSetup(prev => ({
      ...prev,
      departments: [...prev.departments, { ...currentDepartment }]
    }));
    
    setCurrentDepartment({
      name: '',
      classes: [],
      labs: [],
      years: 4,
      sections: [],
      year_subjects: {},  // Year-wise subjects instead of flat subjects array
      year_labs: {}  // Year-wise labs (optional)
    });
  };

  const addClassroom = (type) => {
    const name = prompt(`Enter ${type} name:`);
    if (name) {
      setCurrentDepartment(prev => ({
        ...prev,
        [type]: [...prev[type], { name, capacity: type === 'labs' ? 30 : 60 }]
      }));
    }
  };

  const addSection = () => {
    const sectionName = prompt('Enter section name (e.g., A, B, C):');
    if (!sectionName) return;

    // Create year-specific student counts
    const yearCounts = {};
    const years = currentDepartment.years || 4;

    for (let year = 1; year <= years; year++) {
      const count = prompt(`Enter number of students in Year ${year}, Section ${sectionName}:`);
      if (count !== null) {
        yearCounts[year] = parseInt(count) || 0;
      }
    }

    if (Object.keys(yearCounts).length > 0) {
      setCurrentDepartment(prev => ({
        ...prev,
        sections: [...prev.sections, {
          name: sectionName,
          year_student_counts: yearCounts  // Year-specific student counts
        }]
      }));
    }
  };

  const addSubject = () => {
    const subject = prompt('Enter subject name:');
    if (subject) {
      setCurrentDepartment(prev => ({
        ...prev,
        subjects: [...prev.subjects, subject]
      }));
    }
  };

  const addTeacher = () => {
    if (!currentTeacher.name || !currentTeacher.employee_id || !currentTeacher.department) {
      alert('Please fill in all teacher details');
      return;
    }
    
    setTimetableSetup(prev => ({
      ...prev,
      teachers: [...prev.teachers, { ...currentTeacher }]
    }));
    
    setCurrentTeacher({
      name: '',
      employee_id: '',
      subjects: [],
      department: ''
    });
  };

  const addTeacherSubject = () => {
    const subject = prompt('Enter subject this teacher can teach:');
    if (subject) {
      setCurrentTeacher(prev => ({
        ...prev,
        subjects: [...prev.subjects, subject]
      }));
    }
  };

  const submitTimetableSetup = async () => {
    if (timetableSetup.departments.length === 0) {
      alert('Please add at least one department');
      return;
    }

    if (timetableSetup.teachers.length === 0) {
      alert('Please add at least one teacher');
      return;
    }

    // Validate year_subjects for all departments
    let hasIncompleteSubjects = false;
    timetableSetup.departments.forEach((dept, index) => {
      const totalSubjects = Object.values(dept.year_subjects || {}).reduce((sum, subjects) => sum + subjects.length, 0);
      const expectedSubjects = dept.years * 6;

      if (totalSubjects < expectedSubjects) {
        hasIncompleteSubjects = true;
        alert(`Department ${dept.name}: Please add all ${expectedSubjects} subjects (${expectedSubjects - totalSubjects} remaining)`);
      }
    });

    if (hasIncompleteSubjects) return;

    setLoading(true);
    try {
      // Convert year_subjects and year_labs to arrays for backend
      const setupData = {
        departments: timetableSetup.departments.map(dept => {
          // Convert year_subjects object to simple subjects array
          const allSubjects = [];
          if (dept.year_subjects) {
            Object.values(dept.year_subjects).forEach(yearSubjects => {
              yearSubjects.forEach(subject => {
                if (!allSubjects.includes(subject)) {
                  allSubjects.push(subject);
                }
              });
            });
          }

          // Convert year_labs object to simple labs array
          const allLabs = [];
          if (dept.year_labs) {
            Object.values(dept.year_labs).forEach(yearLabs => {
              yearLabs.forEach(lab => {
                if (!allLabs.includes(lab)) {
                  allLabs.push(lab);
                }
              });
            });
          }

          return {
            name: dept.name,
            classes: dept.classes || [],
            labs: allLabs,  // Use year-wise labs if available, otherwise existing labs
            years: dept.years,
            sections: dept.sections || [],
            year_subjects: dept.year_subjects || {},  // Keep year_subjects for proper backend processing
            year_labs: dept.year_labs || {},  // Keep year_labs for proper backend processing
            subjects: allSubjects  // Convert year_subjects to simple subjects array
          };
        }),
        teachers: timetableSetup.teachers.map(teacher => ({
          name: teacher.name,
          employee_id: teacher.employee_id,
          subjects: teacher.subjects || [],
          department: teacher.department
        }))
      };

      const response = await fetch(`${API_BASE_URL}/timetable/setup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(setupData)
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Timetable setup completed successfully!\n\nSummary:\n- Departments: ${result.departments_created}\n- Teachers: ${result.teachers_created}\n- Students: ${result.students_created}\n- Accounts Created: ${result.users_created}`);

        // Reset form
        setTimetableSetup({
          departments: [],
          teachers: [],
          currentStep: 1,
          totalSteps: 4
        });

        // Fetch updated data
        fetchData(token);

        // Ask if user wants to generate timetable
        if (confirm('Setup completed! Would you like to generate the timetable now?')) {
          generateTimetable();
        }
      } else {
        const error = await response.json();
        alert(`Failed to setup timetable: ${error.detail}`);
      }
    } catch (error) {
      console.error('Timetable setup error:', error);
      alert('Timetable setup failed');
    }
    setLoading(false);
  };

  const generateTimetable = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/timetable/generate`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Timetable generated successfully!\n\nGenerated ${result.entries} timetable entries.`);
        
        // Fetch the updated timetable data
        await fetchTimetableData();
        setCurrentView('timetables');
      } else {
        const error = await response.json();
        alert(`Failed to generate timetable: ${error.detail}`);
      }
    } catch (error) {
      console.error('Timetable generation error:', error);
      alert('Timetable generation failed');
    }
    setLoading(false);
  };

  // Fetch timetable data
  const fetchTimetableData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/timetable/data`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        // Ensure data has proper structure
        setTimetableData({
          departments: data.departments || [],
          teachers: data.teachers || [],
          students: data.students || [],
          timetable: data.timetable || [],
          selectedDepartment: timetableData.selectedDepartment || '',
          selectedYear: timetableData.selectedYear || '',
          selectedSection: timetableData.selectedSection || ''
        });
      }
    } catch (error) {
      console.error('Failed to fetch timetable data:', error);
    }
  };

  // Fetch filtered timetable view
  const fetchTimetableView = async () => {
    try {
      let url = `${API_BASE_URL}/timetable/view`;
      const params = new URLSearchParams();
      
      if (timetableData.selectedDepartment) {
        params.append('department', timetableData.selectedDepartment);
      }
      if (timetableData.selectedYear) {
        params.append('year', timetableData.selectedYear);
      }
      if (timetableData.selectedSection) {
        params.append('section', timetableData.selectedSection);
      }
      
      if (params.toString()) {
        url += `?${params.toString()}`;
      }

      const response = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setTimetableData(prev => ({...prev, timetable: data.timetable}));
      }
    } catch (error) {
      console.error('Failed to fetch timetable view:', error);
    }
  };

  // Export timetable data with constraints information
  const exportTimetableData = () => {
    if (!timetableData.timetable || timetableData.timetable.length === 0) {
      alert('No timetable data to export');
      return;
    }

    const csvContent = [
      ['Day', 'Time', 'Subject', 'Teacher', 'Classroom', 'Department', 'Year', 'Section', 'Type'],
      ...timetableData.timetable.map(entry => [
        entry.day,
        entry.time_slot,
        entry.subject,
        entry.teacher,
        entry.classroom,
        entry.department,
        entry.year,
        entry.section,
        entry.subject === 'Free Period' ? 'Free Period' : 'Scheduled Class'
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `timetable_with_constraints_${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-md w-96">
          <h2 className="text-2xl font-bold mb-6 text-center">Smart Class Scheduler</h2>
          <form onSubmit={login}>
            <div className="mb-4">
              <label className="block text-gray-700 mb-2">Login As</label>
              <div className="flex space-x-4 mb-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="admin"
                    checked={loginForm.role === 'admin'}
                    onChange={(e) => setLoginForm({...loginForm, role: e.target.value})}
                    className="mr-2"
                  />
                  Administrator
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="faculty"
                    checked={loginForm.role === 'faculty'}
                    onChange={(e) => setLoginForm({...loginForm, role: e.target.value})}
                    className="mr-2"
                  />
                  Faculty
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="student"
                    checked={loginForm.role === 'student'}
                    onChange={(e) => setLoginForm({...loginForm, role: e.target.value})}
                    className="mr-2"
                  />
                  Student
                </label>
              </div>
            </div>
            <div className="mb-4">
              <label className="block text-gray-700 mb-2">Username</label>
              <input
                type="text"
                value={loginForm.username}
                onChange={(e) => setLoginForm({...loginForm, username: e.target.value})}
                className="w-full px-3 py-2 border rounded-md"
                placeholder={`Enter ${loginForm.role} username`}
                required
              />
            </div>
            <div className="mb-6">
              <label className="block text-gray-700 mb-2">Password</label>
              <input
                type="password"
                value={loginForm.password}
                onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
                className="w-full px-3 py-2 border rounded-md"
                required
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600 disabled:bg-gray-400"
            >
              {loading ? 'Logging in...' : `Login as ${loginForm.role.charAt(0).toUpperCase() + loginForm.role.slice(1)}`}
            </button>
          </form>
          
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <h1 className="text-2xl font-bold">Smart Class Scheduler</h1>
            <div className="flex items-center space-x-4">
              <span>Welcome, {currentUser?.full_name} ({currentUser?.role})</span>
              <button
                onClick={() => setShowChangePassword(true)}
                className="bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600"
              >
                Change Password
              </button>
              <button
                onClick={logout}
                className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <nav className="mb-8">
          <div className="flex space-x-4">
            <button
              onClick={() => setCurrentView('dashboard')}
              className={`px-4 py-2 rounded-md ${currentView === 'dashboard' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
            >
              Dashboard
            </button>
            
            {/* Show schedule generation for admin and faculty only */}
            {(currentUser?.role === 'admin' || currentUser?.role === 'faculty') && (
              <button
                onClick={() => setCurrentView('generate')}
                className={`px-4 py-2 rounded-md ${currentView === 'generate' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
              >
                Generate Schedule
              </button>
            )}
            
            <button
              onClick={() => setCurrentView('timetables')}
              className={`px-4 py-2 rounded-md ${currentView === 'timetables' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
            >
              Timetables
            </button>
            
            {/* Admin-only sections */}
            {currentUser?.role === 'admin' && (
              <>
                <button
                  onClick={() => setCurrentView('create-timetable')}
                  className={`px-4 py-2 rounded-md ${currentView === 'create-timetable' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
                >
                  Create Timetable
                </button>
                <button
                  onClick={() => setCurrentView('users')}
                  className={`px-4 py-2 rounded-md ${currentView === 'users' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
                >
                  User Management
                </button>
                <button
                  onClick={() => setCurrentView('classrooms')}
                  className={`px-4 py-2 rounded-md ${currentView === 'classrooms' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
                >
                  Classrooms
                </button>
                <button
                  onClick={() => setCurrentView('faculty')}
                  className={`px-4 py-2 rounded-md ${currentView === 'faculty' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
                >
                  Faculty
                </button>
                <button
                  onClick={() => setCurrentView('subjects')}
                  className={`px-4 py-2 rounded-md ${currentView === 'subjects' ? 'bg-blue-500 text-white' : 'bg-gray-200'}`}
                >
                  Subjects
                </button>
              </>
            )}
          </div>
        </nav>

        {/* Change Password Modal */}
        {showChangePassword && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded-lg shadow-lg w-96">
              <h3 className="text-lg font-bold mb-4">Change Password</h3>
              <form onSubmit={changePassword}>
                <div className="mb-4">
                  <label className="block text-gray-700 mb-2">Current Password</label>
                  <input
                    type="password"
                    value={passwordChangeForm.currentPassword}
                    onChange={(e) => setPasswordChangeForm({...passwordChangeForm, currentPassword: e.target.value})}
                    className="w-full px-3 py-2 border rounded-md"
                    required
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-gray-700 mb-2">New Password</label>
                  <input
                    type="password"
                    value={passwordChangeForm.newPassword}
                    onChange={(e) => setPasswordChangeForm({...passwordChangeForm, newPassword: e.target.value})}
                    className="w-full px-3 py-2 border rounded-md"
                    minLength="6"
                    required
                  />
                </div>
                <div className="mb-6">
                  <label className="block text-gray-700 mb-2">Confirm New Password</label>
                  <input
                    type="password"
                    value={passwordChangeForm.confirmPassword}
                    onChange={(e) => setPasswordChangeForm({...passwordChangeForm, confirmPassword: e.target.value})}
                    className="w-full px-3 py-2 border rounded-md"
                    required
                  />
                </div>
                <div className="flex space-x-4">
                  <button
                    type="submit"
                    disabled={loading}
                    className="flex-1 bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600 disabled:bg-gray-400"
                  >
                    {loading ? 'Changing...' : 'Change Password'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowChangePassword(false);
                      setPasswordChangeForm({ currentPassword: '', newPassword: '', confirmPassword: '' });
                    }}
                    className="flex-1 bg-gray-500 text-white py-2 rounded-md hover:bg-gray-600"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {currentView === 'dashboard' && (
          <div className="space-y-8">
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-lg shadow-lg">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-3xl font-bold mb-2">📊 Database Overview</h2>
                  <p className="text-blue-100">Complete view of all data stored in the system</p>
                </div>

                {/* Delete All Button - Admin Only */}
                {currentUser?.role === 'admin' && (
                  <button
                    onClick={() => setShowDeleteAllConfirm(true)}
                    className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg shadow-md transition-colors duration-200 flex items-center gap-2"
                    title="Delete all information and reset system"
                  >
                    <span className="text-xl">🗑️</span>
                    Delete All Information
                  </button>
                )}
              </div>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-1">🏫 Departments</h3>
                    <p className="text-3xl font-bold text-blue-600">{timetableData.departments?.length || 0}</p>
                  </div>
                  <div className="text-blue-500 text-4xl">🏛️</div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-1">👨‍🏫 Teachers</h3>
                    <p className="text-3xl font-bold text-green-600">{timetableData.teachers?.length || 0}</p>
                  </div>
                  <div className="text-green-500 text-4xl">👨‍🎓</div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-purple-500">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-1">👨‍🎓 Students</h3>
                    <p className="text-3xl font-bold text-purple-600">{timetableData.students?.length || 0}</p>
                  </div>
                  <div className="text-purple-500 text-4xl">👥</div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-orange-500">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-1">📅 Timetables</h3>
                    <p className="text-3xl font-bold text-orange-600">{timetableData.timetable?.length || 0}</p>
                  </div>
                  <div className="text-orange-500 text-4xl">📋</div>
                </div>
              </div>
            </div>

            {/* Detailed Data Sections */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

              {/* Departments Section */}
              <div className="bg-white p-6 rounded-lg shadow-md">
                <h3 className="text-xl font-bold mb-4 text-gray-800 border-b-2 border-blue-500 pb-2">
                  🏫 Departments & Year-wise Subjects
                </h3>

                {timetableData.departments?.length > 0 ? (
                  <div className="space-y-4">
                    {timetableData.departments.map((dept, deptIndex) => (
                      <div key={deptIndex} className="border rounded-lg p-4 bg-gray-50">
                        <div className="flex justify-between items-center mb-3">
                          <h4 className="font-bold text-lg text-blue-800">{dept.name}</h4>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => handleEdit(dept, 'department')}
                              className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600"
                            >
                              ✏️ Edit
                            </button>
                            <button
                              onClick={() => handleDelete(dept, 'department')}
                              className="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
                            >
                              🗑️ Delete
                            </button>
                            <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                              {dept.years} Years
                            </span>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 gap-3">
                          {Object.entries(dept.year_subjects || {}).map(([year, subjects]) => (
                            <div key={year} className="bg-white p-3 rounded border-l-4 border-green-500">
                              <div className="flex justify-between items-center mb-2">
                                <span className="font-semibold text-green-800">📖 Year {year}</span>
                                <span className="text-sm text-gray-600">{subjects.length} subjects</span>
                              </div>
                              <div className="flex flex-wrap gap-1">
                                {subjects.map((subject, subjectIndex) => (
                                  <span key={subjectIndex} className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">
                                    {subject}
                                  </span>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>

                        <div className="mt-3 pt-3 border-t border-gray-200">
                          <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="font-semibold text-gray-700">Classrooms:</span>
                              <div className="flex flex-wrap gap-1 mt-1">
                                {dept.classes?.map((cls, index) => (
                                  <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                                    {cls.name} ({cls.capacity})
                                  </span>
                                )) || <span className="text-gray-500">None</span>}
                              </div>
                            </div>
                            <div>
                              <span className="font-semibold text-gray-700">Sections:</span>
                              <div className="flex flex-wrap gap-1 mt-1">
                                {dept.sections?.map((section, index) => (
                                  <span key={index} className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs">
                                    {section.name} ({section.student_count} students)
                                  </span>
                                )) || <span className="text-gray-500">None</span>}
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <div className="text-4xl mb-2">🏫</div>
                    <p>No departments configured</p>
                    <button
                      onClick={() => setCurrentView('create-timetable')}
                      className="mt-2 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 text-sm"
                    >
                      Setup Departments
                    </button>
                  </div>
                )}
              </div>

              {/* Teachers Section */}
              <div className="bg-white p-6 rounded-lg shadow-md">
                <h3 className="text-xl font-bold mb-4 text-gray-800 border-b-2 border-green-500 pb-2">
                  👨‍🏫 Teachers & Subjects
                </h3>

                {timetableData.teachers?.length > 0 ? (
                  <div className="space-y-4">
                    {timetableData.teachers.map((teacher, teacherIndex) => (
                      <div key={teacherIndex} className="border rounded-lg p-4 bg-gray-50">
                        <div className="flex justify-between items-center mb-3">
                          <h4 className="font-bold text-lg text-green-800">
                            {teacher.name}
                          </h4>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => handleEdit(teacher, 'teacher')}
                              className="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
                            >
                              ✏️ Edit
                            </button>
                            <button
                              onClick={() => handleDelete(teacher, 'teacher')}
                              className="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
                            >
                              🗑️ Delete
                            </button>
                            <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">
                              {teacher.employee_id}
                            </span>
                          </div>
                        </div>

                        <div className="mb-3">
                          <span className="font-semibold text-gray-700">Department:</span>
                          <span className="ml-2 text-gray-900">{teacher.department}</span>
                        </div>

                        <div>
                          <span className="font-semibold text-gray-700">Subjects ({teacher.subjects?.length || 0}):</span>
                          <div className="flex flex-wrap gap-1 mt-2">
                            {teacher.subjects?.map((subject, subjectIndex) => (
                              <span key={subjectIndex} className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">
                                {subject}
                              </span>
                            )) || <span className="text-gray-500 italic">No subjects assigned</span>}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <div className="text-4xl mb-2">👨‍🏫</div>
                    <p>No teachers configured</p>
                    <button
                      onClick={() => setCurrentView('create-timetable')}
                      className="mt-2 bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 text-sm"
                    >
                      Setup Teachers
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Students Section */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-xl font-bold mb-4 text-gray-800 border-b-2 border-purple-500 pb-2">
                👨‍🎓 Students Overview
              </h3>

              {timetableData.students?.length > 0 ? (
                <div className="space-y-6">
                  {/* Group students by department */}
                  {Object.entries(
                    timetableData.students.reduce((acc, student) => {
                      const key = student.department;
                      if (!acc[key]) acc[key] = {};
                      if (!acc[key][student.year]) acc[key][student.year] = {};
                      if (!acc[key][student.year][student.section]) acc[key][student.year][student.section] = [];
                      acc[key][student.year][student.section].push(student);
                      return acc;
                    }, {})
                  ).map(([department, years]) => (
                    <div key={department} className="border rounded-lg p-4 bg-gray-50">
                      <h4 className="font-bold text-lg text-purple-800 mb-3">{department}</h4>

                      {Object.entries(years).map(([year, sections]) => (
                        <div key={year} className="ml-4 mb-4">
                          <h5 className="font-semibold text-purple-700 mb-2">📖 Year {year}</h5>

                          {Object.entries(sections).map(([section, students]) => (
                            <div key={section} className="ml-4 bg-white p-3 rounded border-l-4 border-blue-500">
                              <div className="flex justify-between items-center mb-2">
                                <span className="font-medium text-blue-800">Section {section}</span>
                                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                                  {students.length} students
                                </span>
                              </div>

                              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                                {students.map((student, index) => (
                                  <div key={index} className="bg-gray-100 p-3 rounded text-sm border">
                                    <div className="flex justify-between items-center mb-1">
                                      <div className="font-medium">{student.name}</div>
                                      <div className="flex gap-1">
                                        <button
                                          onClick={() => handleEdit(student, 'student')}
                                          className="bg-purple-500 text-white px-2 py-1 rounded text-xs hover:bg-purple-600"
                                        >
                                          ✏️
                                        </button>
                                        <button
                                          onClick={() => handleDelete(student, 'student')}
                                          className="bg-red-500 text-white px-2 py-1 rounded text-xs hover:bg-red-600"
                                        >
                                          🗑️
                                        </button>
                                      </div>
                                    </div>
                                    <div className="text-xs text-gray-600">{student.roll_number}</div>
                                    <div className="text-xs text-gray-500 mt-1">
                                      {student.department} - Year {student.year} - Sec {student.section}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <div className="text-4xl mb-2">👨‍🎓</div>
                  <p>No students configured</p>
                  <p className="text-sm mt-2">Students are automatically created when you set up departments</p>
                </div>
              )}
            </div>

            {/* Timetables Section */}
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-xl font-bold mb-4 text-gray-800 border-b-2 border-orange-500 pb-2">
                📅 Generated Timetables
              </h3>

              {timetableData.timetable?.length > 0 ? (
                <div className="space-y-4">
                  <div className="bg-orange-50 p-4 rounded-lg">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
                      <div>
                        <div className="text-2xl font-bold text-orange-600">{timetableData.timetable.length}</div>
                        <div className="text-sm text-orange-700">Total Entries</div>
                      </div>
                      <div>
                        <div className="text-2xl font-bold text-blue-600">
                          {new Set(timetableData.timetable.map(t => t.department)).size}
                        </div>
                        <div className="text-sm text-blue-700">Departments</div>
                      </div>
                      <div>
                        <div className="text-2xl font-bold text-green-600">
                          {new Set(timetableData.timetable.map(t => t.subject)).size}
                        </div>
                        <div className="text-sm text-green-700">Subjects</div>
                      </div>
                      <div>
                        <div className="text-2xl font-bold text-purple-600">
                          {new Set(timetableData.timetable.map(t => t.teacher)).size}
                        </div>
                        <div className="text-sm text-purple-700">Teachers</div>
                      </div>
                    </div>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full border-collapse border border-gray-300 text-sm">
                      <thead>
                        <tr className="bg-gray-50">
                          <th className="border border-gray-300 p-2 text-center">Day</th>
                          <th className="border border-gray-300 p-2 text-center">Time</th>
                          <th className="border border-gray-300 p-2 text-center">Subject</th>
                          <th className="border border-gray-300 p-2 text-center">Teacher</th>
                          <th className="border border-gray-300 p-2 text-center">Classroom</th>
                          <th className="border border-gray-300 p-2 text-center">Department</th>
                          <th className="border border-gray-300 p-2 text-center">Year</th>
                          <th className="border border-gray-300 p-2 text-center">Section</th>
                        </tr>
                      </thead>
                      <tbody>
                        {timetableData.timetable.slice(0, 50).map((entry, index) => (  // Show first 50 entries
                          <tr key={index} className="hover:bg-gray-50">
                            <td className="border border-gray-300 p-2 text-center capitalize">{entry.day}</td>
                            <td className="border border-gray-300 p-2 text-center">{entry.time_slot}</td>
                            <td className="border border-gray-300 p-2 text-center font-medium">{entry.subject}</td>
                            <td className="border border-gray-300 p-2 text-center">{entry.teacher}</td>
                            <td className="border border-gray-300 p-2 text-center">{entry.classroom}</td>
                            <td className="border border-gray-300 p-2 text-center">{entry.department}</td>
                            <td className="border border-gray-300 p-2 text-center">{entry.year}</td>
                            <td className="border border-gray-300 p-2 text-center">{entry.section}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>

                    {timetableData.timetable.length > 50 && (
                      <div className="text-center mt-4 text-gray-600">
                        <p>Showing first 50 entries of {timetableData.timetable.length} total</p>
                        <button
                          onClick={() => setCurrentView('timetables')}
                          className="mt-2 bg-orange-500 text-white px-4 py-2 rounded hover:bg-orange-600 text-sm"
                        >
                          View All Timetables
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <div className="text-4xl mb-2">📅</div>
                  <p>No timetables generated yet</p>
                  <button
                    onClick={() => setCurrentView('create-timetable')}
                    className="mt-2 bg-orange-500 text-white px-4 py-2 rounded hover:bg-orange-600 text-sm"
                  >
                    Generate Timetable
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {currentView === 'generate' && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-2xl font-bold mb-6">Generate Schedule</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-gray-700 mb-2">Academic Year</label>
                <input
                  type="text"
                  value={academicYear}
                  onChange={(e) => setAcademicYear(e.target.value)}
                  placeholder="2024-2025"
                  className="w-full px-3 py-2 border rounded-md"
                />
              </div>
              <div>
                <label className="block text-gray-700 mb-2">Semester</label>
                <select
                  value={semester}
                  onChange={(e) => setSemester(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md"
                >
                  <option value="">Select Semester</option>
                  <option value="fall">Fall</option>
                  <option value="spring">Spring</option>
                  <option value="summer">Summer</option>
                </select>
              </div>
            </div>

            <div className="mt-6">
              <label className="block text-gray-700 mb-2">Select Subjects</label>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 max-h-64 overflow-y-auto border p-4 rounded-md">
                {subjects.map(subject => (
                  <label key={subject.id} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={selectedSubjects.includes(subject.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedSubjects([...selectedSubjects, subject.id]);
                        } else {
                          setSelectedSubjects(selectedSubjects.filter(id => id !== subject.id));
                        }
                      }}
                      className="mr-2"
                    />
                    {subject.code} - {subject.name}
                  </label>
                ))}
              </div>
            </div>

            <div className="mt-6">
              <button
                onClick={generateSchedule}
                disabled={loading}
                className="bg-green-500 text-white px-6 py-3 rounded-md hover:bg-green-600 disabled:bg-gray-400"
              >
                {loading ? 'Generating...' : 'Generate Schedule'}
              </button>
            </div>
          </div>
        )}

        {currentView === 'schedule-options' && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-2xl font-bold mb-6">Schedule Options</h2>
            {scheduleOptions.length === 0 ? (
              <p>No schedule options available.</p>
            ) : (
              <div className="space-y-6">
                {scheduleOptions.map((option, index) => (
                  <div key={option.id} className="border p-4 rounded-lg">
                    <div className="flex justify-between items-center mb-4">
                      <h3 className="text-xl font-semibold">{option.name}</h3>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => saveTimetable(option)}
                          className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
                        >
                          Save Timetable
                        </button>
                        <span className="text-sm text-gray-600">Score: {option.score.toFixed(1)}</span>
                      </div>
                    </div>

                    {option.conflicts.length > 0 && (
                      <div className="mb-4 p-3 bg-red-100 border border-red-400 rounded">
                        <h4 className="font-semibold text-red-800">Conflicts:</h4>
                        <ul className="list-disc list-inside text-red-700">
                          {option.conflicts.map((conflict, i) => (
                            <li key={i}>{conflict}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="overflow-x-auto">
                      <table className="w-full border-collapse border border-gray-300">
                        <thead>
                          <tr className="bg-gray-50">
                            <th className="border border-gray-300 p-2">Day</th>
                            <th className="border border-gray-300 p-2">Time</th>
                            <th className="border border-gray-300 p-2">Subject</th>
                            <th className="border border-gray-300 p-2">Faculty</th>
                            <th className="border border-gray-300 p-2">Room</th>
                          </tr>
                        </thead>
                        <tbody>
                          {option.schedule.map((entry, i) => (
                            <tr key={i}>
                              <td className="border border-gray-300 p-2 capitalize">{entry.day_of_week}</td>
                              <td className="border border-gray-300 p-2">{entry.start_time} - {entry.end_time}</td>
                              <td className="border border-gray-300 p-2">
                                {subjects.find(s => s.id === entry.subject_id)?.code || entry.subject_id}
                              </td>
                              <td className="border border-gray-300 p-2">
                                {faculty.find(f => f.id === entry.faculty_id)?.name || entry.faculty_id}
                              </td>
                              <td className="border border-gray-300 p-2">
                                {classrooms.find(c => c.id === entry.classroom_id)?.name || entry.classroom_id}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {currentView === 'timetables' && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-2xl font-bold mb-6 text-center">📅 Weekly Timetables</h2>

            {/* Display constraints information */}
            <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-green-50 rounded-lg border-2 border-blue-200">
              <h3 className="text-lg font-bold text-gray-800 mb-3">⚙️ Timetable Generation Constraints</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white p-3 rounded-lg border border-blue-300">
                  <div className="text-sm font-semibold text-blue-800 mb-1">📚 Subject Limits</div>
                  <div className="text-xs text-gray-600">
                    Maximum 5 periods per subject per week
                  </div>
                </div>
                <div className="bg-white p-3 rounded-lg border border-green-300">
                  <div className="text-sm font-semibold text-green-800 mb-1">👨‍🏫 Teacher Limits</div>
                  <div className="text-xs text-gray-600">
                    Maximum 4 periods per teacher per day
                  </div>
                </div>
                <div className="bg-white p-3 rounded-lg border border-purple-300">
                  <div className="text-sm font-semibold text-purple-800 mb-1">🆓 Free Periods</div>
                  <div className="text-xs text-gray-600">
                    Remaining slots are marked as free periods
                  </div>
                </div>
                <div className="bg-white p-3 rounded-lg border border-orange-300">
                  <div className="text-sm font-semibold text-orange-800 mb-1">📅 Schedule</div>
                  <div className="text-xs text-gray-600">
                    5 days (Mon-Fri) × 6 time slots per day
                  </div>
                </div>
              </div>
            </div>
            <div className="mb-6 text-center">
              <button
                onClick={fetchTimetableView}
                className="bg-blue-500 text-white px-6 py-2 rounded-md hover:bg-blue-600 mr-4"
              >
                🔄 Load Timetable Data
              </button>
              <button
                onClick={exportTimetableData}
                className="bg-green-500 text-white px-6 py-2 rounded-md hover:bg-green-600"
              >
                📄 Export All Timetables
              </button>
            </div>
            {timetableData && timetableData.timetable && timetableData.timetable.length > 0 ? (
              <div>
                {/* Group timetables by class (department + year + section) */}
                {(() => {
                  const groupedTimetables = {};
                  
                  timetableData.timetable.forEach(entry => {
                    const classKey = `${entry.department}-Year-${entry.year}-Section-${entry.section}`;
                    if (!groupedTimetables[classKey]) {
                      groupedTimetables[classKey] = {
                        department: entry.department,
                        year: entry.year,
                        section: entry.section,
                        entries: []
                      };
                    }
                    groupedTimetables[classKey].entries.push(entry);
                  });

                  return Object.keys(groupedTimetables).map((classKey, classIndex) => {
                    const classData = groupedTimetables[classKey];
                    const timeSlots = ['9:00-10:00', '10:00-11:00', '11:30-12:30', '12:30-1:30', '2:30-3:30', '3:30-4:30'];
                    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
                    
                    return (
                      <div key={classKey} className="mb-8 p-6 bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl shadow-lg border-2 border-blue-200">
                        {/* Class Header */}
                        <div className="text-center mb-6">
                          <div className="bg-white rounded-lg p-4 shadow-md border-2 border-blue-300">
                            <h3 className="text-2xl font-bold text-blue-800 mb-2">Weekly Timetable</h3>
                            <div className="text-lg font-semibold text-gray-700">
                              {classData.department} - Year {classData.year} - Section {classData.section}
                            </div>
                          </div>
                        </div>

                        {/* Timetable Grid */}
                        <div className="overflow-x-auto">
                          <table className="w-full border-collapse rounded-lg overflow-hidden shadow-lg">
                            <thead>
                              <tr>
                                <th className="bg-gray-200 border-2 border-gray-400 p-3 text-center font-bold text-gray-800">
                                  Time / Day
                                </th>
                                <th className="bg-red-300 border-2 border-red-400 p-3 text-center font-bold text-red-800">
                                  Monday
                                </th>
                                <th className="bg-orange-300 border-2 border-orange-400 p-3 text-center font-bold text-orange-800">
                                  Tuesday
                                </th>
                                <th className="bg-yellow-300 border-2 border-yellow-400 p-3 text-center font-bold text-yellow-800">
                                  Wednesday
                                </th>
                                <th className="bg-green-300 border-2 border-green-400 p-3 text-center font-bold text-green-800">
                                  Thursday
                                </th>
                                <th className="bg-blue-300 border-2 border-blue-400 p-3 text-center font-bold text-blue-800">
                                  Friday
                                </th>
                              </tr>
                            </thead>
                            <tbody>
                              {timeSlots.map((timeSlot, timeIndex) => (
                                <tr key={timeSlot}>
                                  <td className="bg-gray-100 border-2 border-gray-300 p-3 text-center font-semibold text-gray-700">
                                    {timeSlot}
                                  </td>
                                  {days.map((day, dayIndex) => {
                                    const entry = classData.entries.find(
                                      e => e.day === day && e.time_slot === timeSlot
                                    );
                                    
                                    const dayColors = [
                                      'bg-red-100 border-red-200',      // Monday
                                      'bg-orange-100 border-orange-200', // Tuesday  
                                      'bg-yellow-100 border-yellow-200', // Wednesday
                                      'bg-green-100 border-green-200',   // Thursday
                                      'bg-blue-100 border-blue-200'      // Friday
                                    ];
                                    
                                    return (
                                      <td key={day} className={`${dayColors[dayIndex]} border-2 p-3 text-center min-h-[80px]`}>
                                        {entry ? (
                                          <div className="space-y-1">
                                            <div className="font-bold text-gray-800 text-sm">
                                              {safeRender(entry.subject)}
                                            </div>
                                            <div className="text-xs text-gray-600">
                                              {safeRender(entry.teacher)}
                                            </div>
                                            <div className="text-xs text-gray-500">
                                              📍 {safeRender(entry.classroom)}
                                            </div>
                                          </div>
                                        ) : (
                                          <div className="text-gray-400 text-sm">
                                            Free Period
                                          </div>
                                        )}
                                      </td>
                                    );
                                  })}
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>

                        {/* Class Summary */}
                        <div className="mt-4 bg-white rounded-lg p-4 shadow-md">
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
                            <div className="bg-blue-50 p-3 rounded-lg">
                              <div className="text-lg font-bold text-blue-800">
                                {classData.entries.length}
                              </div>
                              <div className="text-sm text-blue-600">Total Classes</div>
                            </div>
                            <div className="bg-green-50 p-3 rounded-lg">
                              <div className="text-lg font-bold text-green-800">
                                {new Set(classData.entries.map(e => e.subject)).size}
                              </div>
                              <div className="text-sm text-green-600">Subjects</div>
                            </div>
                            <div className="bg-purple-50 p-3 rounded-lg">
                              <div className="text-lg font-bold text-purple-800">
                                {new Set(classData.entries.map(e => e.teacher)).size}
                              </div>
                              <div className="text-sm text-purple-600">Teachers</div>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  });
                })()}
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-8 shadow-lg border-2 border-blue-200">
                  <div className="text-6xl mb-4">📅</div>
                  <h3 className="text-xl font-bold text-gray-800 mb-2">No Timetable Data Available</h3>
                  <p className="text-gray-600 mb-6">
                    Create departments and teachers first, then generate beautiful weekly timetables.
                  </p>
                  <button
                    onClick={() => setCurrentView('create-timetable')}
                    className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 font-semibold"
                  >
                    🚀 Create Your First Timetable
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {currentView === 'users' && currentUser?.role === 'admin' && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-2xl font-bold mb-6">User Management</h2>
            <form className="mb-6 p-4 border rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Add New User</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input
                  type="text"
                  placeholder="Username"
                  value={newUserForm.username}
                  onChange={(e) => setNewUserForm({...newUserForm, username: e.target.value})}
                  className="px-3 py-2 border rounded-md"
                />
                <input
                  type="email"
                  placeholder="Email"
                  value={newUserForm.email}
                  onChange={(e) => setNewUserForm({...newUserForm, email: e.target.value})}
                  className="px-3 py-2 border rounded-md"
                />
                <input
                  type="password"
                  placeholder="Password"
                  value={newUserForm.password}
                  onChange={(e) => setNewUserForm({...newUserForm, password: e.target.value})}
                  className="px-3 py-2 border rounded-md"
                />
                <input
                  type="text"
                  placeholder="Full Name"
                  value={newUserForm.fullName}
                  onChange={(e) => setNewUserForm({...newUserForm, fullName: e.target.value})}
                  className="px-3 py-2 border rounded-md"
                />
                <select
                  value={newUserForm.role}
                  onChange={(e) => setNewUserForm({...newUserForm, role: e.target.value})}
                  className="px-3 py-2 border rounded-md"
                >
                  <option value="student">Student</option>
                  <option value="faculty">Faculty</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              <button
                type="button"
                onClick={createUser}
                className="mt-4 bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
              >
                Add User
              </button>
            </form>

            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-gray-300">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="border border-gray-300 p-2">Username</th>
                    <th className="border border-gray-300 p-2">Email</th>
                    <th className="border border-gray-300 p-2">Full Name</th>
                    <th className="border border-gray-300 p-2">Role</th>
                    <th className="border border-gray-300 p-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(user => (
                    <tr key={user.id}>
                      <td className="border border-gray-300 p-2">{user.username}</td>
                      <td className="border border-gray-300 p-2">{user.email}</td>
                      <td className="border border-gray-300 p-2">{user.full_name}</td>
                      <td className="border border-gray-300 p-2">
                        <span className={`px-2 py-1 rounded text-xs ${
                          user.role === 'admin' ? 'bg-red-100 text-red-800' :
                          user.role === 'faculty' ? 'bg-blue-100 text-blue-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                        </span>
                      </td>
                      <td className="border border-gray-300 p-2">
                        {user.id !== currentUser?.id && (
                          <button
                            onClick={() => deleteUser(user.id)}
                            className="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
                          >
                            Delete
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {currentView === 'classrooms' && currentUser?.role === 'admin' && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-2xl font-bold mb-6">Classroom Management</h2>
            <form className="mb-6 p-4 border rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Add New Classroom</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input
                  type="text"
                  placeholder="Room Name"
                  value={newClassroomForm.name}
                  onChange={(e) => setNewClassroomForm({...newClassroomForm, name: e.target.value})}
                  className="px-3 py-2 border rounded-md"
                />
                <input
                  type="number"
                  placeholder="Capacity"
                  value={newClassroomForm.capacity}
                  onChange={(e) => setNewClassroomForm({...newClassroomForm, capacity: e.target.value})}
                  className="px-3 py-2 border rounded-md"
                />
                <input
                  type="text"
                  placeholder="Building"
                  value={newClassroomForm.building}
                  onChange={(e) => setNewClassroomForm({...newClassroomForm, building: e.target.value})}
                  className="px-3 py-2 border rounded-md"
                />
                <input
                  type="number"
                  placeholder="Floor"
                  value={newClassroomForm.floor}
                  onChange={(e) => setNewClassroomForm({...newClassroomForm, floor: e.target.value})}
                  className="px-3 py-2 border rounded-md"
                />
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={newClassroomForm.hasProjector}
                    onChange={(e) => setNewClassroomForm({...newClassroomForm, hasProjector: e.target.checked})}
                    className="mr-2"
                  />
                  Has Projector
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={newClassroomForm.hasComputer}
                    onChange={(e) => setNewClassroomForm({...newClassroomForm, hasComputer: e.target.checked})}
                    className="mr-2"
                  />
                  Has Computer
                </label>
              </div>
              <button
                type="button"
                className="mt-4 bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
              >
                Add Classroom
              </button>
            </form>

            <div className="overflow-x-auto">
              <table className="w-full border-collapse border border-gray-300">
                <thead>
                  <tr className="bg-gray-50">
                    <th className="border border-gray-300 p-2">Name</th>
                    <th className="border border-gray-300 p-2">Capacity</th>
                    <th className="border border-gray-300 p-2">Building</th>
                    <th className="border border-gray-300 p-2">Floor</th>
                    <th className="border border-gray-300 p-2">Facilities</th>
                    <th className="border border-gray-300 p-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {classrooms.map(classroom => (
                    <tr key={classroom.id}>
                      <td className="border border-gray-300 p-2">{classroom.name}</td>
                      <td className="border border-gray-300 p-2">{classroom.capacity}</td>
                      <td className="border border-gray-300 p-2">{classroom.building || '-'}</td>
                      <td className="border border-gray-300 p-2">{classroom.floor || '-'}</td>
                      <td className="border border-gray-300 p-2">
                        {classroom.has_projector && 'Projector '}
                        {classroom.has_computer && 'Computer'}
                      </td>
                      <td className="border border-gray-300 p-2">
                        <button
                          onClick={() => deleteClassroom(classroom.id)}
                          className="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {currentView === 'create-timetable' && (
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-2xl font-bold mb-6">Create Comprehensive Timetable System</h2>
            
            <div className="mb-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold">Setup Progress</h3>
                <span className="text-sm text-gray-600">
                  Departments: {timetableSetup.departments.length} | Teachers: {timetableSetup.teachers.length}
                </span>
              </div>
            </div>

            {/* Department Setup Section */}
            <div className="mb-8 p-4 border rounded-lg">
              <h3 className="text-xl font-semibold mb-4">📚 Department Setup</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-gray-700 mb-2">Department Name</label>
                  <input
                    type="text"
                    value={currentDepartment.name}
                    onChange={(e) => setCurrentDepartment({...currentDepartment, name: e.target.value})}
                    className="w-full px-3 py-2 border rounded-md"
                    placeholder="e.g., Computer Science"
                  />
                </div>
                <div>
                  <label className="block text-gray-700 mb-2">Number of Years</label>
                  <select
                    value={currentDepartment.years}
                    onChange={(e) => setCurrentDepartment({...currentDepartment, years: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border rounded-md"
                  >
                    <option value={3}>3 Years</option>
                    <option value={4}>4 Years</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-gray-700 mb-2">Classrooms</label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {currentDepartment.classes && currentDepartment.classes.length > 0 ? 
                      currentDepartment.classes.map((classroom, index) => {
                        const displayText = classroom && typeof classroom === 'object' 
                          ? `${classroom.name || 'Unnamed'} (${classroom.capacity || 0})` 
                          : String(classroom || 'Unknown');
                        return (
                          <span key={index} className="bg-blue-100 px-2 py-1 rounded text-sm">
                            {displayText}
                          </span>
                        );
                      })
                      : <span className="text-gray-500 text-sm">No classrooms added</span>
                    }
                  </div>
                  <button
                    onClick={() => addClassroom('classes')}
                    className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600"
                  >
                    Add Classroom
                  </button>
                </div>
                <div>
                  <label className="block text-gray-700 mb-2">Labs</label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {currentDepartment.labs && currentDepartment.labs.length > 0 ? 
                      currentDepartment.labs.map((lab, index) => {
                        const displayText = lab && typeof lab === 'object' 
                          ? `${lab.name || 'Unnamed'} (${lab.capacity || 0})` 
                          : String(lab || 'Unknown');
                        return (
                          <span key={index} className="bg-green-100 px-2 py-1 rounded text-sm">
                            {displayText}
                          </span>
                        );
                      })
                      : <span className="text-gray-500 text-sm">No labs added</span>
                    }
                  </div>
                  <button
                    onClick={() => addClassroom('labs')}
                    className="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
                  >
                    Add Lab
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-gray-700 mb-2">Sections with Year-wise Student Counts</label>
                  <div className="flex flex-wrap gap-2 mb-2">
                    {currentDepartment.sections && currentDepartment.sections.length > 0 ? 
                      currentDepartment.sections.map((section, index) => {
                        const displayText = section && typeof section === 'object' 
                          ? (() => {
                              const years = currentDepartment.years || 4;
                              const counts = [];
                              for (let year = 1; year <= years; year++) {
                                const count = section.year_student_counts?.[year] || 0;
                                counts.push(`Y${year}:${count}`);
                              }
                              return `${section.name || 'Unnamed'} (${counts.join(', ')} students)`;
                            })()
                          : String(section || 'Unknown');
                        return (
                          <span key={index} className="bg-yellow-100 px-2 py-1 rounded text-sm">
                            {displayText}
                          </span>
                        );
                      })
                      : <span className="text-gray-500 text-sm">No sections added</span>
                    }
                  </div>
                  <button
                    onClick={addSection}
                    className="bg-yellow-500 text-white px-3 py-1 rounded text-sm hover:bg-yellow-600"
                  >
                    Add Section
                  </button>
                </div>
                <div>
                  <label className="block text-gray-700 mb-2">Year-wise Subjects</label>
                  <div className="space-y-3">
                    {Array.from({length: currentDepartment.years}, (_, yearIndex) => {
                      const yearNumber = yearIndex + 1;
                      const yearSubjects = currentDepartment.year_subjects?.[yearNumber] || [];

                      return (
                        <div key={yearNumber} className="border rounded-lg p-3 bg-gray-50">
                          <div className="flex justify-between items-center mb-2">
                            <h4 className="font-semibold text-sm">📖 Year {yearNumber} Subjects</h4>
                            <span className="text-xs text-gray-600">({yearSubjects.length}/6 subjects)</span>
                          </div>

                          <div className="flex flex-wrap gap-2 mb-2">
                            {yearSubjects.map((subject, subjectIndex) => (
                              <span key={subjectIndex} className="bg-purple-100 px-2 py-1 rounded text-sm">
                                {subject}
                              </span>
                            ))}
                          </div>

                          <div className="flex gap-2">
                            <input
                              type="text"
                              placeholder={`Add Year ${yearNumber} Subject`}
                              className="flex-1 px-2 py-1 text-sm border rounded"
                              onKeyPress={(e) => {
                                if (e.key === 'Enter' && e.target.value.trim()) {
                                  const newSubjects = {...currentDepartment.year_subjects};
                                  if (!newSubjects[yearNumber]) newSubjects[yearNumber] = [];
                                  if (!newSubjects[yearNumber].includes(e.target.value.trim())) {
                                    newSubjects[yearNumber] = [...newSubjects[yearNumber], e.target.value.trim()];
                                    setCurrentDepartment({...currentDepartment, year_subjects: newSubjects});
                                  }
                                  e.target.value = '';
                                }
                              }}
                            />
                            <button
                              onClick={() => {
                                const input = document.querySelector(`input[placeholder="Add Year ${yearNumber} Subject"]`);
                                if (input && input.value.trim()) {
                                  const newSubjects = {...currentDepartment.year_subjects};
                                  if (!newSubjects[yearNumber]) newSubjects[yearNumber] = [];
                                  if (!newSubjects[yearNumber].includes(input.value.trim())) {
                                    newSubjects[yearNumber] = [...newSubjects[yearNumber], input.value.trim()];
                                    setCurrentDepartment({...currentDepartment, year_subjects: newSubjects});
                                  }
                                  input.value = '';
                                }
                              }}
                              className="bg-purple-500 text-white px-2 py-1 rounded text-sm hover:bg-purple-600"
                            >
                              Add
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {(() => {
                    const totalSubjects = Object.values(currentDepartment.year_subjects || {}).reduce((sum, subjects) => sum + subjects.length, 0);
                    const expectedSubjects = currentDepartment.years * 6;
                    const progress = (totalSubjects / expectedSubjects) * 100;

                    return (
                      <div className="mt-3">
                        <div className="flex justify-between text-sm text-gray-600 mb-1">
                          <span>Subject Setup Progress</span>
                          <span>{totalSubjects}/{expectedSubjects} subjects</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-purple-500 h-2 rounded-full transition-all duration-300"
                            style={{width: `${Math.min(progress, 100)}%`}}
                          ></div>
                        </div>
                        {totalSubjects < expectedSubjects && (
                          <p className="text-xs text-orange-600 mt-1">
                            ⚠️ Add {expectedSubjects - totalSubjects} more subjects for complete setup
                          </p>
                        )}
                        {totalSubjects >= expectedSubjects && (
                          <p className="text-xs text-green-600 mt-1">
                            ✅ All subjects configured! Ready to add department.
                          </p>
                        )}
                      </div>
                    );
                  })()}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-gray-700 mb-2">Year-wise Labs with Duration (Optional)</label>
                  <div className="space-y-3">
                    {Array.from({length: currentDepartment.years}, (_, yearIndex) => {
                      const yearNumber = yearIndex + 1;
                      const yearLabs = currentDepartment.year_labs?.[yearNumber] || [];

                      return (
                        <div key={yearNumber} className="border rounded-lg p-3 bg-gray-50">
                          <div className="flex justify-between items-center mb-2">
                            <h4 className="font-semibold text-sm">🧪 Year {yearNumber} Labs</h4>
                            <span className="text-xs text-gray-600">({yearLabs.length} labs)</span>
                          </div>

                          <div className="flex flex-wrap gap-2 mb-2">
                            {yearLabs.map((lab, labIndex) => (
                              <span key={labIndex} className="bg-orange-100 px-2 py-1 rounded text-sm">
                                {typeof lab === 'object' ? `${lab.name} (${lab.periods} periods)` : lab}
                              </span>
                            ))}
                          </div>

                          <div className="flex gap-2 mb-2">
                            <input
                              type="text"
                              id={`lab-name-${yearNumber}`}
                              placeholder={`Lab Name`}
                              className="flex-1 px-2 py-1 text-sm border rounded"
                            />
                            <select
                              id={`lab-periods-${yearNumber}`}
                              className="px-2 py-1 text-sm border rounded"
                              defaultValue="2"
                            >
                              <option value="1">1 Period</option>
                              <option value="2">2 Periods</option>
                              <option value="3">3 Periods</option>
                              <option value="4">4 Periods</option>
                            </select>
                            <button
                              onClick={() => {
                                const nameInput = document.getElementById(`lab-name-${yearNumber}`);
                                const periodsSelect = document.getElementById(`lab-periods-${yearNumber}`);
                                const labName = nameInput?.value.trim();
                                const periods = parseInt(periodsSelect?.value || 2);

                                if (labName) {
                                  const newLabs = {...currentDepartment.year_labs};
                                  if (!newLabs[yearNumber]) newLabs[yearNumber] = [];

                                  // Check if lab already exists
                                  const existingLab = newLabs[yearNumber].find(lab =>
                                    typeof lab === 'object' ? lab.name === labName : lab === labName
                                  );

                                  if (!existingLab) {
                                    newLabs[yearNumber] = [...newLabs[yearNumber], {
                                      name: labName,
                                      periods: periods
                                    }];
                                    setCurrentDepartment({...currentDepartment, year_labs: newLabs});
                                  }

                                  nameInput.value = '';
                                  periodsSelect.value = '2';
                                }
                              }}
                              className="bg-orange-500 text-white px-3 py-1 rounded text-sm hover:bg-orange-600"
                            >
                              Add Lab
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {(() => {
                    const totalLabs = Object.values(currentDepartment.year_labs || {}).reduce((sum, labs) => sum + labs.length, 0);

                    return (
                      <div className="mt-3">
                        <div className="flex justify-between text-sm text-gray-600 mb-1">
                          <span>Lab Setup Progress</span>
                          <span>{totalLabs} labs configured</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-orange-500 h-2 rounded-full transition-all duration-300"
                            style={{width: `${Math.min(totalLabs * 10, 100)}%`}}
                          ></div>
                        </div>
                        {totalLabs > 0 && (
                          <p className="text-xs text-green-600 mt-1">
                            ✅ Labs configured for {Object.keys(currentDepartment.year_labs || {}).length} year(s)
                          </p>
                        )}
                      </div>
                    );
                  })()}
                </div>
              </div>

              <button
                onClick={addDepartment}
                className="bg-indigo-500 text-white px-4 py-2 rounded-md hover:bg-indigo-600"
                disabled={!currentDepartment.name}
              >
                Add Department
              </button>
            </div>

            {/* Teacher Setup Section */}
            <div className="mb-8 p-4 border rounded-lg">
              <h3 className="text-xl font-semibold mb-4">👨‍🏫 Teacher Setup</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <label className="block text-gray-700 mb-2">Teacher Name</label>
                  <input
                    type="text"
                    value={currentTeacher.name}
                    onChange={(e) => setCurrentTeacher({...currentTeacher, name: e.target.value})}
                    className="w-full px-3 py-2 border rounded-md"
                    placeholder="e.g., Dr. John Smith"
                  />
                </div>
                <div>
                  <label className="block text-gray-700 mb-2">Employee ID</label>
                  <input
                    type="text"
                    value={currentTeacher.employee_id}
                    onChange={(e) => setCurrentTeacher({...currentTeacher, employee_id: e.target.value})}
                    className="w-full px-3 py-2 border rounded-md"
                    placeholder="e.g., EMP001"
                  />
                </div>
                <div>
                  <label className="block text-gray-700 mb-2">Department</label>
                  <select
                    value={currentTeacher.department}
                    onChange={(e) => setCurrentTeacher({...currentTeacher, department: e.target.value})}
                    className="w-full px-3 py-2 border rounded-md"
                  >
                    <option value="">Select Department</option>
                    {timetableSetup.departments.map((dept, index) => (
                      <option key={index} value={dept.name}>{dept.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="mb-4">
                <label className="block text-gray-700 mb-2">Subjects Teacher Can Handle</label>

                {/* Show available subjects from all years */}
                {timetableSetup.departments.length > 0 && (
                  <div className="mb-3 p-3 bg-blue-50 rounded-lg">
                    <h4 className="font-semibold text-sm mb-2">📚 Available Subjects by Year:</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {timetableSetup.departments.map((dept, deptIndex) => {
                        const yearSubjects = dept.year_subjects || {};
                        return Object.entries(yearSubjects).map(([year, subjects]) => (
                          <div key={`${deptIndex}-${year}`} className="text-xs">
                            <span className="font-medium">{dept.name} Year {year}:</span>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {subjects.map((subject, subjectIndex) => (
                                <span key={subjectIndex} className="bg-blue-100 px-1 py-0.5 rounded text-xs">
                                  {subject}
                                </span>
                              ))}
                            </div>
                          </div>
                        ));
                      })}
                    </div>
                  </div>
                )}

                <div className="flex flex-wrap gap-2 mb-2">
                  {currentTeacher.subjects && currentTeacher.subjects.length > 0 ?
                    currentTeacher.subjects.map((subject, index) => {
                      const displayText = subject && typeof subject === 'object'
                        ? String(subject.name || 'Unnamed Subject')
                        : String(subject || 'Unknown');
                      return (
                        <span key={index} className="bg-orange-100 px-2 py-1 rounded text-sm">
                          {displayText}
                        </span>
                      );
                    })
                    : <span className="text-gray-500 text-sm">No subjects added</span>
                  }
                </div>

                {/* Available subjects for quick selection */}
                {timetableSetup.departments.length > 0 && currentTeacher.department && (
                  <div className="mt-2">
                    <label className="block text-gray-600 text-xs mb-1">Quick Add from Available Subjects:</label>
                    <div className="flex flex-wrap gap-1">
                      {(() => {
                        // Get all subjects from the selected department
                        const dept = timetableSetup.departments.find(d => d.name === currentTeacher.department);
                        if (!dept || !dept.year_subjects) return null;

                        const allSubjects = [];
                        Object.entries(dept.year_subjects).forEach(([year, subjects]) => {
                          subjects.forEach(subject => {
                            if (!allSubjects.includes(subject)) {
                              allSubjects.push(subject);
                            }
                          });
                        });

                        return allSubjects.map((subject, index) => (
                          <button
                            key={index}
                            onClick={() => {
                              if (!currentTeacher.subjects.includes(subject)) {
                                setCurrentTeacher({
                                  ...currentTeacher,
                                  subjects: [...currentTeacher.subjects, subject]
                                });
                              }
                            }}
                            className="bg-gray-100 hover:bg-gray-200 px-2 py-1 rounded text-xs border"
                          >
                            + {subject}
                          </button>
                        ));
                      })()}
                    </div>
                  </div>
                )}

                <button
                  onClick={addTeacherSubject}
                  className="bg-orange-500 text-white px-3 py-1 rounded text-sm hover:bg-orange-600"
                >
                  Add Subject
                </button>
              </div>

              <button
                onClick={addTeacher}
                className="bg-teal-500 text-white px-4 py-2 rounded-md hover:bg-teal-600"
                disabled={!currentTeacher.name || !currentTeacher.employee_id || !currentTeacher.department}
              >
                Add Teacher
              </button>
            </div>

            {/* Summary Section */}
            {(timetableSetup.departments.length > 0 || timetableSetup.teachers.length > 0) && (
              <div className="mb-8 p-4 bg-gray-50 rounded-lg">
                <h3 className="text-xl font-semibold mb-4">📋 Setup Summary</h3>
                
                {timetableSetup.departments.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-semibold mb-2">Departments ({timetableSetup.departments.length}):</h4>
                    {timetableSetup.departments.map((dept, index) => (
                      <div key={index} className="mb-2 p-2 bg-white rounded border">
                        <strong>{dept.name}</strong> - {dept.years} years, {dept.sections.length} sections, {Object.values(dept.year_subjects || {}).reduce((sum, subjects) => sum + subjects.length, 0)} subjects
                        <br />
                        <small className="text-gray-600">
                          Classes: {dept.classes.length} | Labs: {dept.labs.length} | 
                          Total Students: {dept.sections.reduce((sum, section) => sum + (section.student_count || 0), 0)}
                        </small>
                      </div>
                    ))}
                  </div>
                )}

                {timetableSetup.teachers.length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-semibold mb-2">Teachers ({timetableSetup.teachers.length}):</h4>
                    {timetableSetup.teachers.map((teacher, index) => (
                      <div key={index} className="mb-2 p-2 bg-white rounded border">
                        <strong>{teacher.name}</strong> ({teacher.employee_id}) - {teacher.department}
                        <br />
                        <small className="text-gray-600">
                          Subjects: {teacher.subjects && teacher.subjects.length > 0 
                            ? teacher.subjects.map(s => {
                                if (s && typeof s === 'object') {
                                  return String(s.name || 'Unnamed');
                                }
                                return String(s || 'Unknown');
                              }).join(', ')
                            : 'No subjects assigned'
                          }
                        </small>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Submit Section */}
            <div className="flex justify-between items-center">
              <div className="text-sm text-gray-600">
                <p>This will automatically:</p>
                <ul className="list-disc list-inside ml-4">
                  <li>Generate student roll numbers</li>
                  <li>Create login accounts for all faculty and students</li>
                  <li>Set default passwords (Employee ID for faculty, Roll Number for students)</li>
                  <li>Prepare the system for timetable generation</li>
                </ul>
              </div>
              
              <button
                onClick={submitTimetableSetup}
                disabled={loading || timetableSetup.departments.length === 0 || timetableSetup.teachers.length === 0}
                className="bg-green-500 text-white px-6 py-3 rounded-md hover:bg-green-600 disabled:bg-gray-400"
              >
                {loading ? 'Setting up...' : 'Complete Setup & Create Accounts'}
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Edit Modal */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-md max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-bold mb-4">
              Edit {editingItem?.type?.charAt(0).toUpperCase() + editingItem?.type?.slice(1)}
            </h3>

            <form onSubmit={(e) => { e.preventDefault(); saveEdit(); }}>
              {editingItem?.type === 'department' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Department Name</label>
                    <input
                      type="text"
                      value={editForm.name || ''}
                      onChange={(e) => setEditForm({...editForm, name: e.target.value})}
                      className="w-full px-3 py-2 border rounded-md"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Years</label>
                    <input
                      type="number"
                      value={editForm.years || ''}
                      onChange={(e) => setEditForm({...editForm, years: parseInt(e.target.value)})}
                      className="w-full px-3 py-2 border rounded-md"
                      min="1"
                      max="6"
                      required
                    />
                  </div>
                </div>
              )}

              {editingItem?.type === 'teacher' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Teacher Name</label>
                    <input
                      type="text"
                      value={editForm.name || ''}
                      onChange={(e) => setEditForm({...editForm, name: e.target.value})}
                      className="w-full px-3 py-2 border rounded-md"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Employee ID</label>
                    <input
                      type="text"
                      value={editForm.employee_id || ''}
                      onChange={(e) => setEditForm({...editForm, employee_id: e.target.value})}
                      className="w-full px-3 py-2 border rounded-md"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Department</label>
                    <input
                      type="text"
                      value={editForm.department || ''}
                      onChange={(e) => setEditForm({...editForm, department: e.target.value})}
                      className="w-full px-3 py-2 border rounded-md"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Subjects (comma-separated)</label>
                    <input
                      type="text"
                      value={editForm.subjects?.join(', ') || ''}
                      onChange={(e) => setEditForm({...editForm, subjects: e.target.value.split(',').map(s => s.trim()).filter(s => s)})}
                      className="w-full px-3 py-2 border rounded-md"
                      placeholder="Subject1, Subject2, Subject3"
                    />
                  </div>
                </div>
              )}

              {editingItem?.type === 'student' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Student Name</label>
                    <input
                      type="text"
                      value={editForm.name || ''}
                      onChange={(e) => setEditForm({...editForm, name: e.target.value})}
                      className="w-full px-3 py-2 border rounded-md"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Roll Number</label>
                    <input
                      type="text"
                      value={editForm.roll_number || ''}
                      onChange={(e) => setEditForm({...editForm, roll_number: e.target.value})}
                      className="w-full px-3 py-2 border rounded-md"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Department</label>
                    <input
                      type="text"
                      value={editForm.department || ''}
                      onChange={(e) => setEditForm({...editForm, department: e.target.value})}
                      className="w-full px-3 py-2 border rounded-md"
                      required
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-1">Year</label>
                      <input
                        type="number"
                        value={editForm.year || ''}
                        onChange={(e) => setEditForm({...editForm, year: parseInt(e.target.value)})}
                        className="w-full px-3 py-2 border rounded-md"
                        min="1"
                        max="6"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">Section</label>
                      <input
                        type="text"
                        value={editForm.section || ''}
                        onChange={(e) => setEditForm({...editForm, section: e.target.value})}
                        className="w-full px-3 py-2 border rounded-md"
                        required
                      />
                    </div>
                  </div>
                </div>
              )}

              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => {
                    setShowEditModal(false);
                    setEditingItem(null);
                    setEditForm({});
                  }}
                  className="px-4 py-2 text-gray-600 border rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-gray-400"
                >
                  {loading ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && deleteItem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-md">
            <h3 className="text-xl font-bold mb-4 text-red-600">⚠️ Confirm Delete</h3>

            <div className="mb-6">
              <p className="mb-3">
                Are you sure you want to delete this {deleteItem.type}?
              </p>

              <div className="bg-gray-50 p-3 rounded border">
                {deleteItem.type === 'department' && (
                  <div>
                    <strong>Department:</strong> {deleteItem.name}<br/>
                    <small className="text-gray-600">
                      This will also delete all associated teachers, students, and timetable entries.
                    </small>
                  </div>
                )}
                {deleteItem.type === 'teacher' && (
                  <div>
                    <strong>Teacher:</strong> {deleteItem.name}<br/>
                    <strong>Employee ID:</strong> {deleteItem.employee_id}<br/>
                    <small className="text-gray-600">
                      This will remove the teacher from all timetable entries.
                    </small>
                  </div>
                )}
                {deleteItem.type === 'student' && (
                  <div>
                    <strong>Student:</strong> {deleteItem.name}<br/>
                    <strong>Roll Number:</strong> {deleteItem.roll_number}<br/>
                    <small className="text-gray-600">
                      This will permanently remove the student from the system.
                    </small>
                  </div>
                )}
              </div>
            </div>

            <div className="flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowDeleteConfirm(false);
                  setDeleteItem(null);
                }}
                className="px-4 py-2 text-gray-600 border rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                disabled={loading}
                className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 disabled:bg-gray-400"
              >
                {loading ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete All Confirmation Modal */}
      {showDeleteAllConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-lg">
            <h3 className="text-xl font-bold mb-4 text-red-600">🚨 CONFIRM COMPLETE SYSTEM RESET</h3>

            <div className="mb-6">
              <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-4">
                <div className="flex items-start">
                  <span className="text-red-500 text-2xl mr-3">⚠️</span>
                  <div>
                    <h4 className="font-bold text-red-800 mb-2">This action will permanently delete:</h4>
                    <ul className="text-sm text-red-700 space-y-1">
                      <li>• 🏫 All departments and their configurations</li>
                      <li>• 👨‍🏫 All teachers and their assignments</li>
                      <li>• 👨‍🎓 All students and their records</li>
                      <li>• 📅 All generated timetables and schedules</li>
                      <li>• 🔐 All user credentials (except admin1)</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 mb-4">
                <div className="flex items-start">
                  <span className="text-yellow-500 text-xl mr-3">💾</span>
                  <div>
                    <h4 className="font-bold text-yellow-800 mb-1">Data Summary:</h4>
                    <p className="text-sm text-yellow-700">
                      • Departments: {timetableData.departments?.length || 0}<br/>
                      • Teachers: {timetableData.teachers?.length || 0}<br/>
                      • Students: {timetableData.students?.length || 0}<br/>
                      • Timetables: {timetableData.timetable?.length || 0}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-blue-50 border-l-4 border-blue-500 p-4">
                <div className="flex items-start">
                  <span className="text-blue-500 text-xl mr-3">ℹ️</span>
                  <div>
                    <h4 className="font-bold text-blue-800 mb-1">What will be preserved:</h4>
                    <p className="text-sm text-blue-700">
                      • Your admin account (admin1)<br/>
                      • System configuration and settings<br/>
                      • This action cannot be undone
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowDeleteAllConfirm(false)}
                className="px-4 py-2 text-gray-600 border rounded-md hover:bg-gray-50"
                disabled={deleteAllLoading}
              >
                Cancel
              </button>
              <button
                onClick={confirmDeleteAll}
                disabled={deleteAllLoading}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:bg-gray-400 flex items-center gap-2"
              >
                {deleteAllLoading ? (
                  <>
                    <span className="animate-spin">🔄</span>
                    Resetting...
                  </>
                ) : (
                  <>
                    <span>🗑️</span>
                    Delete All & Reset
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
