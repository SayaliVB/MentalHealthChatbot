import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/Sidebar.css';

const GLOBAL_IP = 'http://localhost:5001';

const Sidebar = ({ 
  userName = 'User', 
  clearChat,
  setMessages,
  messages,
  userLocation,
  setCrisisEvents
}) => {
  const navigate = useNavigate(); 

  const handleLogout = () => {
    localStorage.clear(); 
    navigate('/'); 
  };

  const handleSendTherapistLocator = async () => {
    const question = "find nearest therapists";
    const newMessage = { id: Date.now(), text: question, sender: 'user' };
    setMessages(prev => [...prev, newMessage]);
  
    // Send request to backend
    try {
      const response = await fetch(`${GLOBAL_IP}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          lat: userLocation.lat,
          lng: userLocation.lng,
          history: [...messages, newMessage],
          userName: localStorage.getItem("username") || "User",
          culture: localStorage.getItem("culture") || "Unknown",
          user_id: parseInt(localStorage.getItem("userId")) || 0,
        }),
      });
  
      const data = await response.json();
      const aiResponse = {
        id: Date.now() + 1,
        text: data.response || "Sorry, I couldn't find therapists right now.",
        sender: 'ai',
      };
  
      setMessages(prev => [...prev, aiResponse]);
  
      if (data.isCrisis === true) {
        setCrisisEvents(prev => [...prev, {
          response: data.response,
          therapist_contacted: false,
          timestamp: new Date().toISOString(),
        }]);
      }
  
    } catch (error) {
      console.error("Error fetching therapist info:", error);
      setMessages(prev => [...prev, {
        id: Date.now() + 2,
        text: "Error finding therapists near your location.",
        sender: 'ai',
      }]);
    }
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
          <div onClick={clearChat} style={{ cursor: 'pointer' }}>💬 New Chat</div>
          <div onClick={() => navigate('/profile')} style={{ cursor: 'pointer' }}>👤 Profile Management</div>
          <div onClick={() => handleSendTherapistLocator()} style={{ cursor: 'pointer' }}> 📍 Therapist Locator</div>
        </div>
      </div>

      <div className="sidebar-footer">
        <button className="logout-btn"onClick={handleLogout}>🔓 Logout</button>
      </div>
    </div>
  );
};

export default Sidebar;
