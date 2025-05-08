import React, { useState, useRef, useEffect } from 'react';
import '../styles/ChatArea.css';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';   


const GLOBAL_IP = 'http://localhost:5001';

const ChatArea = ({ userName = "User", isTTS, messages,setMessages,crisisEvents,setCrisisEvents}) => {
  // const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const bottomRef = useRef(null);
  // const [crisisEvents, setCrisisEvents] = useState([]);
  const [isListening, setIsListening] = useState(false);

  const playTTS = (text) => {
    if (!window.speechSynthesis) {
      alert('TTS not supported in this browser.');
      return;
    }
    if (speechSynthesis.speaking) {
      speechSynthesis.cancel();
      return; // If already speaking, stop and return
    }
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    utterance.pitch = 1;
    utterance.rate = 1;
    speechSynthesis.speak(utterance);
  };
  

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
 
  
  // const handleSend = async () => {
  //   if (input.trim()) {
  //     const newMessage = { id: Date.now(), text: input, sender: 'user' };
  //     const updatedMessages = [...messages, newMessage];
  //     setMessages(updatedMessages);
  //     setInput('');

  //     try {
  //       const response = await fetch("${GLOBAL_IP}/chat", {
  //         method: "POST",
  //         headers: { "Content-Type": "application/json" },
  //         body: JSON.stringify({
  //           question: input,
  //           history: updatedMessages, // ✅ Send actual message buffer, not joined string
  //           userName: localStorage.getItem("username") || "User",
  //           culture: localStorage.getItem("culture") || "Unknown"
  //         }),
  //       });

  //       const data = await response.json();
  //       const aiResponse = {
  //         id: Date.now() + 1,
  //         text: data.response || "Sorry, I didn't get that.",
  //         sender: 'ai',
  //       };

  //       if (data.isCrisis === true) {
  //         setCrisisEvents((prev) => [...prev, {
  //           response: data.response,
  //           therapist_contacted: false,
  //           timestamp: new Date().toISOString(),
  //         }]);
  //       }

  //       if (isTTS) {
  //         playTTS(aiResponse.text);
  //       }

  //       setMessages((prev) => [...prev, aiResponse]);

  //     } catch (error) {
  //       console.error("Error fetching response:", error);
  //       const errorMessage = {
  //         id: Date.now() + 1,
  //         text: "Error connecting to the chatbot.",
  //         sender: 'ai',
  //       };
  //       setMessages((prev) => [...prev, errorMessage]);
  //     }
  //   }
  // };
  
   // 🎙 Speech to Text Function
   const handleSpeech = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  
    if (!SpeechRecognition) {
      alert('Speech recognition not supported in this browser.');
      return;
    }
  
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.start();
    setIsListening(true);  
  
    recognition.onresult = (event) => {
      const speechResult = event.results[0][0].transcript;
      setInput(speechResult);
      setIsListening(false);  
    };
  
    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      alert('Speech recognition failed. Please try again.');
      setIsListening(false);  
    };
  
    recognition.onend = () => {
      setIsListening(false);
    };
  };
  

  const handleSend = async () => {
    if (input.trim()) {
      const newMessage = { id: Date.now(), text: input, sender: 'user' };
      const updatedMessages = [...messages, newMessage];
      setMessages(updatedMessages);
      setInput('');
  
      const loweredInput = input.toLowerCase().trim();
  
      // Special case for "find nearest therapists"
      if (loweredInput === "find nearest therapists") {
        navigator.geolocation.getCurrentPosition(async (position) => {
          const lat = position.coords.latitude;
          const lng = position.coords.longitude;
  
          try {
            const response = await fetch(`${GLOBAL_IP}/chat`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                question: input,
                lat,
                lng,
                history: updatedMessages,
                userName: localStorage.getItem("username") || "User",
                culture: localStorage.getItem("culture") || "Unknown",
                // user_id: localStorage.getItem("user_id") || "Unknown",
                id: parseInt(localStorage.getItem("id")) || 0,
              }),
            });
  
            const data = await response.json();
            const aiResponse = {
              id: Date.now() + 1,
              text: data.response || "Sorry, I couldn't find therapists right now.",
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
            console.error("Error fetching nearest therapists:", error);
            setMessages((prev) => [...prev, {
              id: Date.now() + 1,
              text: "Error finding therapists near your location.",
              sender: 'ai',
            }]);
          }
        }, (error) => {
          console.error("Geolocation error:", error);
          setMessages((prev) => [...prev, {
            id: Date.now() + 1,
            text: "Location access is required to find nearby therapists.",
            sender: 'ai',
          }]);
        });
  
      } else {
        // 🧠 Normal chat handling
        try {
          const response = await fetch(`${GLOBAL_IP}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              question: input,
              history: updatedMessages,
              userName: localStorage.getItem("username") || "User",
              culture: localStorage.getItem("culture") || "Unknown", 
              user_id: parseInt(localStorage.getItem("userId")) || 0,
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
          setMessages((prev) => [...prev, {
            id: Date.now() + 1,
            text: "Error connecting to the chatbot.",
            sender: 'ai',
          }]);
        }
      }
    }
  };
  

 
  const handleEndChat = async () => {

      try {
        console.log("Chat History:", messages);
        const response = await fetch(`${GLOBAL_IP}/store_chat_summary`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            userid: localStorage.getItem("userId"),
            chatHistory: messages,
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
    
    setCrisisEvents([]);
    setMessages([]);
  };

  return (
    <div className="chat-area">
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
            {msg.sender === 'ai' ? (
              <div className="bubble-with-button">
                <div className="chat-bubble">
                  <ReactMarkdown rehypePlugins={[rehypeRaw]}>{msg.text}</ReactMarkdown>
                </div>
                <button 
                  onClick={() => playTTS(msg.text)} 
                  className="tts-button"
                  title="Listen to this response"
                >
                  <img 
                    src="/icons/speaker.png" 
                    alt="Listen" 
                    style={{ width: '25px', height: '25px' }}
                  />
                </button>
              </div>
            ) : (
              <div className="chat-bubble">
                <ReactMarkdown>{msg.text}</ReactMarkdown>
              </div>
            )}
            
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="chat-input-container">
        <input
          type="text"
          className="chat-input"
          placeholder="Ask about your mental health..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
        />
        <button onClick={handleSpeech} className="mic-button">
          {isListening ? '🎙️ Listening...' : '🎤 Speak'}
        </button>
        <button onClick={handleSend} className="send-button">Send</button>
        <button onClick={handleEndChat} className="send-button">End Chat</button>
      </div>
    </div>
  );
};

export default ChatArea;
