import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import ChatArea from '../components/ChatArea';
import CrisisButton from '../components/CrisisButton';
import SettingsModal from '../components/SettingsModal';
import '../styles/ChatDashboard.css';

const ChatDashboard = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [userName, setUserName] = useState('');

  useEffect(() => {
    const storedName = localStorage.getItem('username');
    if (storedName) setUserName(storedName);
  }, []);

  const toggleDarkMode = () => setIsDarkMode(prev => !prev);

  return (
    <div className={`dashboard-container ${isDarkMode ? 'dark' : ''}`}>
      <Sidebar />
      <div className="main-content">
        <Header userName={userName} onOpenSettings={() => setIsModalOpen(true)} />

        {isModalOpen && (
          <SettingsModal
            onClose={() => setIsModalOpen(false)}
            onToggleDarkMode={toggleDarkMode}
            isDarkMode={isDarkMode}
            userName={userName}
          />
        )}

        <ChatArea />
        <CrisisButton />
      </div>
    </div>
  );
};

export default ChatDashboard;
