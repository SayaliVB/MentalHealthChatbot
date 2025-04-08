import React from 'react';
import '../styles/ChatArea.css';

const ChatArea = ({ userName = "User" }) => {
  return (
    <div className="chat-area">
      {/* Summary Box */}
      <div className="summary-card">
        The user expressed feelings of loneliness... (summary here)
      </div>

      {/* Bot Welcome Message */}
      <div className="chat-message bot">
      <img
          src="https://cdn-icons-png.flaticon.com/128/9193/9193824.png"
          alt="Bot Avatar"
          className="chat-avatar"
       />

        <div className="chat-bubble">
          Hello {userName}! I'm here to support your mental health journey. 😊
        </div>
      </div>

      {/* Input Form */}
      <div className="chat-input-container">
        <input
          type="text"
          className="chat-input"
          placeholder="Ask about your mental health..."
        />
        <button className="send-button">Send</button>
      </div>

    </div>
  );
};

export default ChatArea;
