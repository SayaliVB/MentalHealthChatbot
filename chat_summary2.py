import streamlit as st
from streamlit_chat import message
from openai import OpenAI
import psycopg2
import os

# OpenAI API Key - Replace with your actual key
api_key="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"


# PostgreSQL connection details - Replace with your actual database credentials
DB_NAME = "demodb"
DB_USER = "postgres"
DB_PASSWORD = "Divija@1998"
DB_HOST = "localhost"
DB_PORT = "5432"

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Streamlit UI - Title
st.title("🧘 Mental Health ChatBot 🤗")

# Function to fetch past chat summary
def fetch_chat_summary(user_id):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cursor = conn.cursor()
        query = "SELECT session_summary FROM chat_sessions WHERE user_id = %s ORDER BY timestamp DESC LIMIT 1"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        st.error(f"Database Error: {e}")
        return None

# Function to store chat summary in PostgreSQL
def store_chat_summary(user_id, messages):
    summary = summarize_chat(messages)
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cursor = conn.cursor()
        query = "INSERT INTO chat_sessions (user_id, session_summary) VALUES (%s, %s)"
        cursor.execute(query, (user_id, summary))
        conn.commit()
        cursor.close()
        conn.close()
        st.success("✅ Chat summary saved successfully!")
    except Exception as e:
        st.error(f"Database Error: {e}")

# Function to summarize chat session using GPT
def summarize_chat(messages):
    prompt = f"""
    You are a mental health chatbot that summarizes user conversations in a few sentences. 
    Focus on the user's emotional state, concerns, and key advice given.

    Chat Transcript:
    {messages}

    Provide a concise and human-friendly summary:
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=200,
        temperature=0.5
    )
    return response.choices[0].message.content.strip()

# Function to initialize session state
def initialize_session_state(user_id):
    if "history" not in st.session_state:
        st.session_state["history"] = []

    if "past_summary" not in st.session_state:
        st.session_state["past_summary"] = fetch_chat_summary(user_id) or "No previous session data."

# Function to handle chatbot response
def conversation_chat(user_id, question):
    past_summary = st.session_state["past_summary"]

    prompt = f"""
    You are a compassionate, supportive, and friendly **mental health chatbot**. 
    Your primary goal is to provide **empathetic and helpful** responses, similar to a caring friend. 
    You should **never** say that you "cannot help" or "cannot provide support." Instead:

    - Offer **kind and comforting words**.
    - Suggest **practical coping techniques** (e.g., mindfulness, grounding exercises, deep breathing).
    - Encourage **healthy activities** (e.g., journaling, talking to a friend, listening to music).
    - Help the user feel **understood and not alone**.
    - **Only recommend seeking professional help if the user explicitly talks about self-harm or crisis.**

    Past Chat Summary (if relevant):
    {past_summary}

    User's Message:
    "{question}"

    Chatbot Response (empathetic and detailed, NO generic "I can't help" statements):
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=250,
        temperature=0.7
    )

    bot_response = response.choices[0].message.content.strip()
    
    # Append user input and chatbot response to history
    st.session_state["history"].append({"user": question, "bot": bot_response})
    return bot_response

# Initialize session state for user
user_id = 1  # Static for now, replace with actual user ID
initialize_session_state(user_id)

# Streamlit Chat UI with Improved Display
st.subheader("💬 Chat with Me")
chat_container = st.container()

# Display chat history in a structured conversation format
with chat_container:
    for chat in st.session_state["history"]:
        with st.chat_message("user"):
            st.markdown(f"**You:** {chat['user']}")
        with st.chat_message("assistant"):
            st.markdown(f"**🤖 Chatbot:** {chat['bot']}")

# User input field
user_input = st.text_input("Type your message...", key="input", placeholder="Ask about your mental health")

if st.button("Send") and user_input:
    chatbot_response = conversation_chat(user_id, user_input)
    
    # Display user message
    with chat_container:
        with st.chat_message("user"):
            st.markdown(f"**You:** {user_input}")
        with st.chat_message("assistant"):
            st.markdown(f"**🤖 Chatbot:** {chatbot_response}")

    # Refresh UI to clear input field and update chat display
    st.rerun()  # ✅ Fix: Replaces st.experimental_rerun()

# Save chat summary when user ends session
if st.button("End Chat Session"):
    store_chat_summary(user_id, [chat["user"] for chat in st.session_state["history"]])
    st.session_state["history"] = []  # Clear chat history for new session
    st.success("📝 Chat session ended. Summary saved!")
