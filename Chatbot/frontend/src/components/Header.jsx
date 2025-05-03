import React from 'react';
import '../styles/Header.css';

const Header = ({ isTTS, toggleTTS }) => {
  return (
    <header className="header">
      <div>🧠 Mental Health ChatBot – Your AI Support Companion</div>
      {/* <div className="tts-toggle">
        <label htmlFor="ttsToggle">🔊 TTS</label>
        <input
          type="checkbox"
          id="ttsToggle"
          checked={isTTS}
          onChange={toggleTTS}
        />
      </div> */}
    </header>
  );
};

export default Header;
