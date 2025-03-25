import React from 'react';

const Sidebar = () => {
  // Dummy chat history list
  const chatHistory = [
    { id: 1, title: 'Chat with Dr. Smith' },
    { id: 2, title: 'Session 2: Coping Strategies' },
    { id: 3, title: 'Group Support Chat' },
  ];

  return (
    <aside className="sidebar">
      <button className="new-chat-button">+ New Chat</button>
      <h3>Chat History</h3>
      <ul>
        {chatHistory.map((chat) => (
          <li key={chat.id}>{chat.title}</li>
        ))}
      </ul>
    </aside>
  );
}  

export default Sidebar;
