# 📘 Empower Mental Health Chatbot

🧠 A culturally sensitive AI-powered mental health chatbot using LangChain, GPT-4, Pinecone, and Flask. Developed as a master's capstone project at San José State University.

---

## 📌 Project Overview

This chatbot addresses global mental health challenges by:

- Offering culturally personalized responses  
- Supporting crisis detection and escalation  
- Integrating retrieval-augmented generation (RAG) using Pinecone  
- Enabling real-time voice/text interaction with TTS/STT  
- Logging sessions for therapist reviews and continuity  

📝 **Final Report Reference:**  
See Chapter 1: Introduction, Goals, and Contributions  

---

## 🏗️ Architecture Overview

📊 **Refer to Report: Chapter 2 – Project Architecture**

```
Frontend (React) <--> Flask Backend (LangChain + GPT-4) <--> PostgreSQL + Pinecone
                    ↳ Tools: PineconeSearch | WebSearch | ChatSummary | NearestTherapist
```

- Routing Agent: Dynamically selects tools or raw LLM  
- Tool-Enhanced Responses: Used for verified advice, cultural grounding, therapist lookup  
- Raw GPT-4 Responses: Used when personal empathy is more helpful  
- Dual Path Ranking: GPT-4 ranks both responses for final reply  

---

## 🔍 Component Mapping to Report

| Component | Description | Code Path | Report Chapter |
|----------|-------------|-----------|----------------|
| Frontend | Chat UI with voice input, TTS playback, therapist map | `frontend/components/` | Ch. 4.1, 5.1 |
| Chatbot Logic | Core LLM flow, RAG, prompt building, ranking | `backend/chatbot_logic.py` | Ch. 2.2.3, 5.2.1 |
| Crisis Detection | BERT + GPT logic to detect emotional danger | `chatbot_logic.py` | Ch. 2.2.2, 4.2.3 |
| Router Agent | Orchestrates tool usage with LangChain | `backend/agents/router_agent.py` | Ch. 2.2.4, 4.2.1 |
| Pinecone Search Tool | Vector DB lookup using OpenAI embeddings | `backend/tools/pinecone_search_tool.py` | Ch. 4.2.2, 5.3.2 |
| Web Search Tool | DuckDuckGo real-time fallback | `tools/web_search_tool.py`, `web_search_beautiful.py` | Ch. 3.3.3 |
| Chat Summary Tool | Fetches previous summaries for continuity | `tools/chat_summary_tool.py` | Ch. 5.2.3 |
| Therapist Locator | Google Maps API to suggest local help | `tools/nearest_therapist_tool.py` | Ch. 2.2.6, 5.3.3 |
| Memory Buffer | Stores prior chat context in session | `utils/memory_manager.py` | Ch. 3.3.1 |
| Session API | User auth, chat summary, therapist API | `backend/api_for_db.py` | Ch. 5.2.3 |
| Data Embedding | Indexes JSON, PDF, scraped content | `pinecone_rag.py` | Ch. 5.3.5 |
| PostgreSQL Setup | Stores users, chats, crisis logs, therapists | `backend/connection.py` | Ch. 4.3.1 |
| Speech Modules | STT (browser-based), TTS (gTTS) | `ChatArea.jsx`, `chatbot_logic.py` | Ch. 5.1.2 |
| Security | bcrypt password hashing, CORS, JWT-ready | `api_for_db.py`, `.env` | Ch. 5.3.4 |

---

## 💬 Features

| Feature | Description |
|--------|-------------|
| 🧠 Cultural Personalization | Tailors prompts based on selected user culture |
| 🔍 RAG + Pinecone | Search vector DBs for CBT, PHQ-9, Indian context, SAMHSA |
| 📢 TTS & 🎙️ STT | Accessible speech input/output |
| 🚨 Crisis Detection | Escalates emergencies with 988 lifeline + therapist map |
| 📍 Therapist Locator | Uses Google Maps API to suggest nearby help |
| 📝 Session Summaries | GPT-4 creates summaries for therapist review |
| 🧰 Agent Tool Routing | LangChain agent selects tools dynamically |
| 🔒 Secure Auth | Login/signup with hashed password & safe routing |

---

## 🚀 Setup Instructions

### 📦 1. Backend Setup (Flask)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**Environment variables (.env):**
```ini
OPENAI_API_KEY=your_key
PINECONE_API_KEY=your_key
VITE_GOOGLE_MAPS_API_KEY=your_key
```

Start the API:
```bash
python api_for_db.py
```

---

### 🌐 2. Frontend Setup (React + Vite)

```bash
cd frontend
npm install
npm run dev
npm install rehype-raw
```

Make sure the Flask backend is running on `localhost:5001`.

---

## 🧪 Testing

- ✅ 50 Test cases for Routing Agent – 88% accuracy  
- ✅ 50 Crisis Detection inputs – 94% accuracy  
- ✅ GPT-4 Evaluator scores (Empathy, Safety, Fluency)  
- ✅ Manual testing: TTS, STT, Therapist Locator  
- ✅ UI/UX tested across browsers and devices  

---

## 📊 Dataset Overview

📚 **Mapped to Report Section 5.3.5**

| Dataset Type | Description | Pinecone Namespace |
|--------------|-------------|--------------------|
| 🇮🇳 Indian Cultural Context | Family, beliefs, collectivism | `indian_culture` |
| 📘 SAMHSA Guidelines | Clinical treatments & meds | `samhsa_guidelines` |
| 💬 Forum Chat Logs | Empathetic support examples | `chat_logs` |
| 🧠 CBT Techniques | 15 strategies for mental health | `cbt_techniques` |
| 📄 PHQ-9 | 9-point depression scale | `phq9_intents` |
| 🌐 Web-Scraped Info | WHO, NIMH, VeryWellMind | `web_anxiety`, etc. |

---

## 📤 Deployment Notes

- Currently tested on **localhost**
- Future-ready for deployment on **Heroku**, **Render**, or **AWS**
- Requires `.env` for OpenAI, Pinecone, and Google Maps API keys

---

## 🔚 Authors & Credits

**👩‍💻 Team Members:**  
Sai Pranavi Kurapati, Sayali Bayaskar, Divija Choudhary, Armaghan Abtahi

**📖 Advisor:**  
Professor Kaikai Liu

📄 **Final Report (PDF)**  
📦 GitHub Repo: https://github.com/SayaliVB/MentalHealthChatbot
