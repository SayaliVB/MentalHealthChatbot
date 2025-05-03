import React from 'react';

const CrisisButton = ({ onClick }) => {
  return (
    <div className="crisis-button-container">
      <button onClick={onClick} className="crisis-button">
        🆘 Immediate Help
      </button>
    </div>
  );
};

export default CrisisButton;
