import React from 'react';

const CrisisButton = () => {
  const handleCrisisConnect = () => {
    // This would be the logic to connect to real-time crisis management helper
    alert('Connecting to crisis management support...');
  };

  return (
    <div className="crisis-button-container">
      <button onClick={handleCrisisConnect} className="crisis-button">
        Need Immediate Help?
      </button>
    </div>
  );
};

export default CrisisButton;
