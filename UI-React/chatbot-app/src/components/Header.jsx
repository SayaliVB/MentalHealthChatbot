import React, { useState } from 'react';
import SettingsModal from './SettingsModal';
import '../styles/Header.css'

const Header = ({ userName, onOpenSettings }) => {
    return (
      <header className="dashboard-header">
        <div className="profile-info">
          <span>Welcome, {userName || "Guest"}</span>
        </div>
        <div className="settings">
          <button onClick={onOpenSettings}>Settings</button>
        </div>
      </header>
    );
  };
  
  export default Header;
  