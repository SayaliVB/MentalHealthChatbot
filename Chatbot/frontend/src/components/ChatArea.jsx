import React, { useState, useRef, useEffect } from 'react';
import '../styles/ChatArea.css';

const ChatArea = ({ userName = "User", isTTS }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const bottomRef = useRef(null);
  const [crisisEvents, setCrisisEvents] = useState([]);

  const playTTS = (text) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    speechSynthesis.speak(utterance);
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

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

        if (data.isCrisis === true) {
          setCrisisEvents((prev) => [...prev, {
            response: data.response,
            therapist_contacted: false,
            timestamp: new Date().toISOString(),
          }]);
        }

        if (isTTS) {
          playTTS(aiResponse.text);
        }

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

  const handleEndChat = async () => {
    try {
      const response = await fetch("http://localhost:5000/store_chat_summary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userid: localStorage.getItem("userId"),
          chatHistory: messages,
          crisisEvents: crisisEvents,
        }),
      });
      if (response.ok) {
        setCrisisEvents([]);
      }
    } catch (error) {
      console.error("Error storing chat summary:", error);
    }
  };

  return (
    <div className="chat-area">
      {/* <div className="summary-card">
        The user expressed feelings of loneliness... (summary here)
      </div> */}

      {/* Chat Messages Scrollable */}
      <div className="chat-messages-container">
        {messages.map((msg) => (
          <div key={msg.id} className={`chat-message ${msg.sender}`}>
            {msg.sender === 'ai' && (
              <img
                src="https://cdn-icons-png.flaticon.com/128/9193/9193824.png"
                alt="Bot Avatar"
                className="chat-avatar"
              />
            )}
            <div className="chat-bubble">{msg.text}</div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {/* Input Form Fixed */}
      <div className="chat-input-container">
        <input
          type="text"
          className="chat-input"
          placeholder="Ask about your mental health..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />
        <button onClick={handleSend} className="send-button">Send</button>
        <button onClick={handleEndChat} className="send-button">End Chat</button>
      </div>
    </div>
  );
};

export default ChatArea;