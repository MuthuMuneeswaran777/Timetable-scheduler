import React from "react";
import { Routes, Route } from "react-router-dom";
import Header from "./Header.jsx";
import AdminDashboard from "../pages/AdminDashboard.jsx";
import TeacherManagement from "../pages/TeacherManagement.jsx";
import TimetableBuilder from "../pages/TimetableBuilder.jsx";
import DataManager from "../pages/DataManager.jsx";

const Dashboard = () => {
  return (
    <div>
      <Header />
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
  );
};

export default Dashboard;
