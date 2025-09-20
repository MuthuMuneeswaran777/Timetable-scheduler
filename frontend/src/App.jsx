import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import ErrorBoundary from "./components/ErrorBoundary.jsx";
import Login from "./pages/Login.jsx";
import ChangePassword from "./pages/ChangePassword.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import Dashboard from "./components/Dashboard.jsx";

function App() {
	console.log('App component rendering...');
	
	return (
		<ErrorBoundary>
			<BrowserRouter>
				<div className="min-h-screen bg-gray-50 text-gray-900">
					<Routes>
						{/* Public Routes */}
						<Route path="/login" element={<Login />} />
						
						{/* Protected Routes */}
						<Route path="/change-password" element={
							<ProtectedRoute>
								<ChangePassword />
							</ProtectedRoute>
						} />
						
						{/* Dashboard and all protected routes */}
						<Route path="/dashboard/*" element={
							<ProtectedRoute>
								<Dashboard />
							</ProtectedRoute>
						} />
						
						{/* Root redirect */}
						<Route path="/" element={<Navigate to="/dashboard" replace />} />
					</Routes>
				</div>
			</BrowserRouter>
		</ErrorBoundary>
	);
}

export default App;
