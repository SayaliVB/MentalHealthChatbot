import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/Sidebar.css';

const Sidebar = ({ userName = 'User' }) => {
  const navigate = useNavigate(); 

  const handleLogout = () => {
    localStorage.clear(); 
    navigate('/'); 
  };

  return (
    <div className="sidebar">
      <div className="sidebar-content">
        <div className="profile">
          <img src="https://cdn-icons-png.flaticon.com/512/2206/2206368.png" alt="User Icon" />
          <p><strong>Welcome, {userName}</strong></p>
          <p>(Mental Wellness Seeker)</p>
        </div>

        <div className="chat-history">
          <div>💬 New Chat</div>
          <div>📈 Analytics Dashboard</div>
          <div>👤 Profile Management</div>
          <div>📍 Therapist Locator</div>
        </div>
      </div>

      <div className="sidebar-footer">
        <button className="logout-btn"onClick={handleLogout}>🔓 Logout</button>
      </div>
    </div>
  );
};

export default Sidebar;
