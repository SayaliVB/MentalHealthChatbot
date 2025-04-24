import React from 'react';
import '../styles/SettingsModal.css';

const SettingsModal = ({ onClose, onToggleDarkMode, isDarkMode, userName }) => {
    return (
      <div className="modal-overlay">
        <div className="settings-modal">
          <h2>Settings</h2>
  
          <div className="setting-item">
            <label>Dark Mode</label>
            <input
              type="checkbox"
              checked={isDarkMode}
              onChange={onToggleDarkMode}
            />
          </div>
  
          <div className="setting-item">
            <label>User Profile</label>
            <p>{userName}</p>
          </div>
  
          <button className="close-button" onClick={onClose}>Close</button>
        </div>
      </div>
    );
  };
  
  export default SettingsModal;