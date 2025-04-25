import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import ChatArea from '../components/ChatArea';
import CrisisButton from '../components/CrisisButton';
import SettingsModal from '../components/SettingsModal';
import MapModal from '../components/MapModal'; // New modal for doctors
import '../styles/ChatDashboard.css';

const ChatDashboard = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [showMapModal, setShowMapModal] = useState(false);
  const [userLocation, setUserLocation] = useState({ lat: 37.7749, lng: -122.4194 }); // Default: SF
  const [userName, setUserName] = useState('');
  // for TTS the user can toggle it on and off
  const [isTTS, setIsTTS] = useState(false);
  const toggleTTS = () => setIsTTS(prev => !prev);

  // Get user name and location on mount
  useEffect(() => {
    const storedName = localStorage.getItem('username');
    if (storedName) setUserName(storedName);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setUserLocation({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        });
      },
      () => console.warn("Geolocation not available or denied.")
    );
  }, []);

  const toggleDarkMode = () => setIsDarkMode(prev => !prev);
  const handleShowImmediateHelp = () => setShowMapModal(true);
  const handleCloseMapModal = () => setShowMapModal(false);

  return (
    <div className={`dashboard-container ${isDarkMode ? 'dark' : ''}`}>
      <Sidebar userName={userName} />

      <div className="main-content">
        {/* <Header userName={userName} onOpenSettings={() => setIsModalOpen(true)} /> */}
        <Header userName={userName} onOpenSettings={() => setIsModalOpen(true)} isTTS={isTTS} toggleTTS={toggleTTS} />
        {isModalOpen && (
          <SettingsModal
            onClose={() => setIsModalOpen(false)}
            onToggleDarkMode={toggleDarkMode}
            isDarkMode={isDarkMode}
            userName={userName}
          />
        )}

         {/* Chat area for user interaction with tts */}
         {/* <ChatArea userName={userName} /> */}
        <ChatArea userName={userName} isTTS={isTTS} />

        {/* Immediate Help button */}
        <CrisisButton onClick={handleShowImmediateHelp} />

        {/* Modal for Google Map and Helplines */}
        {showMapModal && (
          <MapModal onClose={handleCloseMapModal} userLocation={userLocation} />
        )}
      </div>
    </div>
  );
};

export default ChatDashboard;
