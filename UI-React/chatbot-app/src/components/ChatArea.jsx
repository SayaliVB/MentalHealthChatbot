import React, { useState } from 'react';

const ChatArea = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const handleSend = async () => {
    if (input.trim()) {
      const newMessage = { id: Date.now(), text: input, sender: 'user' };
      setMessages((prev) => [...prev, newMessage]);
      setInput('');
  
      try {
        const response = await fetch("http://localhost:5000/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            question: input,
            history: messages.map(msg => `${msg.sender === 'user' ? 'User' : 'Bot'}: ${msg.text}`).join("\n")
          }),
        });
  
        const data = await response.json();
        const aiResponse = {
          id: Date.now() + 1,
          text: data.response || "Sorry, I didn't get that.",
          sender: 'ai',
        };
        setMessages((prev) => [...prev, aiResponse]);
      } catch (error) {
        console.error("Error fetching response:", error);
        const errorMessage = {
          id: Date.now() + 1,
          text: "Error connecting to the chatbot.",
          sender: 'ai',
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    }
  };
  

  return (
    <div className="chat-area">
      <div className="messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
      </div>
      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask your question..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
};

export default ChatArea;
