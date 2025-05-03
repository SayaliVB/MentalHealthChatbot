import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import SignIn from "./pages/SignIn";
import ChatDashboard from "./pages/ChatDashboard";
import Profile from "./pages/Profile";
import './App.css'

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/login" />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signin" element={<SignIn />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/dashboard" element={<ChatDashboard />} />
      </Routes>
    </Router>
  );
};

export default App;
