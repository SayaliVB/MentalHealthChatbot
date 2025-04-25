import React, { useState } from 'react';
import '../styles/ChatArea.css';

const ChatArea = ({ userName = "User", isTTS  }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  // play tts if the user has enabled it
  const playTTS = (text) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    speechSynthesis.speak(utterance);
  };
  //crisis detection
  const [crisisEvents, setCrisisEvents] = useState([]);

  
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
        // Crisis detection logic now in correct place
        console.log("AI Response:", data.response);
        console.log("isCrisis:", data.isCrisis);
        if (data.isCrisis === true) {
          setCrisisEvents((prev) => {
            const updated = [
              ...prev,
              {
                response: data.response,
                therapist_contacted: false,
                timestamp: new Date().toISOString(),
              }
            ];
            console.log("Crisis Detected! Updated crisisEvents:", updated);
            return updated;
          });
        }
        if (isTTS) {
          console.log("Playing TTS for:", aiResponse.text);
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
      console.log("Chat History:", messages);
      const response = await fetch("http://localhost:5000/store_chat_summary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          userid: localStorage.getItem("userId"),
          chatHistory: messages,
          //pass the crisis events to the backend
          crisisEvents: crisisEvents,
        }),
      });
      if (response.ok) {
        console.log("Summary and crisis events sent successfully.");
        // Clear crisis events after storing
        setCrisisEvents([]);
      }
  
    } catch (error) {
      console.error("Error storing chat summary:", error);
    }
  };

  return (
    <div className="chat-area">
      {/* Summary Box */}
      <div className="summary-card">
        The user expressed feelings of loneliness... (summary here)
      </div>

      {/* Chat Messages */}
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

      {/* Input Form */}
      <div className="chat-input-container">
        <input
          type="text"
          className="chat-input"
          placeholder="Ask about your mental health..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <button onClick={handleSend} className="send-button">Send</button>
        <button onClick={handleEndChat} className="send-button">End Chat</button>
      </div>
    </div>
  );
};

export default ChatArea;
