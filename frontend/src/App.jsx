import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import AdminDashboard from "./pages/AdminDashboard.jsx";
import TeacherManagement from "./pages/TeacherManagement.jsx";
import TimetableBuilder from "./pages/TimetableBuilder.jsx";
import DataManager from "./pages/DataManager.jsx";

function App() {
	return (
		<BrowserRouter>
			<div className="min-h-screen bg-gray-50 text-gray-900">
				<header className="border-b bg-white">
					<div className="mx-auto max-w-7xl px-4 py-3 flex items-center justify-between">
						<h1 className="text-lg font-semibold">Timetable Manager</h1>
						<nav className="flex gap-4 text-sm">
							<NavLink to="/" end className={({ isActive }) => `px-3 py-2 rounded-md ${isActive ? "bg-gray-900 text-white" : "hover:bg-gray-100"}`}>Dashboard</NavLink>
							<NavLink to="/teachers" className={({ isActive }) => `px-3 py-2 rounded-md ${isActive ? "bg-gray-900 text-white" : "hover:bg-gray-100"}`}>Teachers</NavLink>
							<NavLink to="/batches" className={({ isActive }) => `px-3 py-2 rounded-md ${isActive ? "bg-gray-900 text-white" : "hover:bg-gray-100"}`}>Batches</NavLink>
							<NavLink to="/subjects" className={({ isActive }) => `px-3 py-2 rounded-md ${isActive ? "bg-gray-900 text-white" : "hover:bg-gray-100"}`}>Subjects</NavLink>
							<NavLink to="/offerings" className={({ isActive }) => `px-3 py-2 rounded-md ${isActive ? "bg-gray-900 text-white" : "hover:bg-gray-100"}`}>Offerings</NavLink>
							<NavLink to="/rooms" className={({ isActive }) => `px-3 py-2 rounded-md ${isActive ? "bg-gray-900 text-white" : "hover:bg-gray-100"}`}>Rooms</NavLink>
							<NavLink to="/builder" className={({ isActive }) => `px-3 py-2 rounded-md ${isActive ? "bg-gray-900 text-white" : "hover:bg-gray-100"}`}>Builder</NavLink>
						</nav>
					</div>
				</header>
				<main className="mx-auto max-w-7xl px-4 py-6">
					<Routes>
						<Route path="/" element={<AdminDashboard />} />
						<Route path="/teachers" element={<TeacherManagement />} />
						<Route path="/batches" element={<DataManager entity="batches" />} />
						<Route path="/subjects" element={<DataManager entity="subjects" />} />
						<Route path="/offerings" element={<DataManager entity="subject_offerings" />} />
						<Route path="/rooms" element={<DataManager entity="rooms" />} />
						<Route path="/builder" element={<TimetableBuilder />} />
					</Routes>
				</main>
			</div>
		</BrowserRouter>
	);
}

export default App;
