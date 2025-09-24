import React from "react";
import { Routes, Route } from "react-router-dom";
import Header from "./Header.jsx";
import AdminDashboard from "../pages/AdminDashboard.jsx";
import TeacherManagement from "../pages/TeacherManagement.jsx";
import TimetableBuilder from "../pages/TimetableBuilder.jsx";
import EnhancedDataManager from "../pages/EnhancedDataManager.jsx";

const Dashboard = () => {
  return (
    <div>
      <Header />
      <main className="mx-auto max-w-7xl px-4 py-6">
        <Routes>
          <Route path="/" element={<AdminDashboard />} />
          <Route path="/teachers" element={<TeacherManagement />} />
          <Route path="/batches" element={<EnhancedDataManager entity="batches" />} />
          <Route path="/subjects" element={<EnhancedDataManager entity="subjects" />} />
          <Route path="/offerings" element={<EnhancedDataManager entity="subject_offerings" />} />
          <Route path="/rooms" element={<EnhancedDataManager entity="rooms" />} />
          <Route path="/builder" element={<TimetableBuilder />} />
        </Routes>
      </main>
    </div>
  );
};

export default Dashboard;
