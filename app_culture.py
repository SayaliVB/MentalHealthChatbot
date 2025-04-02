from http import client
import psycopg2
import requests
import streamlit as st
from streamlit_chat import message
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentType
import os
import json
from sentence_transformers import SentenceTransformer, util
from langchain.schema.runnable import RunnableSequence
from PyPDF2 import PdfReader
from web_search_beautiful import fetch_info_for
from openai import OpenAI

os.environ["TOKENIZERS_PARALLELISM"] = "false"

query_params = st.query_params
user = query_params.get("user", "Guest")  # Default to "Guest" if not found
user_id = query_params.get("userid", 0)

# Load and parse the JSON file
def load_json_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

json_data = load_json_data('data/json_dataset.json')

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def chunk_text(text, chunk_size=500):
    words = text.split()
    chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

pdf_path = 'data/Indian_culture.pdf'
pdf_text = extract_text_from_pdf(pdf_path)
pdf_chunks = chunk_text(pdf_text)
pdf_embeddings = [embedding_model.encode(chunk) for chunk in pdf_chunks]

llm = ChatOpenAI(
    temperature=0.6,
    api_key="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"
)

def safe_fetch_info(query):
    
    fallback_keys = {
    "anxiety": "anxiety",
    "depression": "depression",
    "stress": "stress",
    "burnout": "burnout",
    "ptsd": "ptsd",
    "exam": "exam stress"
    }

    key = None
    for k in fallback_keys:
        if k in query.lower():
            key = fallback_keys[k]
            break
    if key is None:
        return "No trusted information available for this topic."
    return fetch_info_for(key)

tools = [
    Tool.from_function(
        name="fetch_info_for",
        func=safe_fetch_info,
        description="Fetch mental health info on anxiety or depression from trusted websites."
    )
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

st.title("Mental Health ChatBot 🤗")
global_ip = '127.0.0.1:5000'

def fetch_chat_summary(user_id):
    response = requests.post(f'http://{global_ip}/get_chat_summary', json={"user_id": user_id}, headers={'Content-Type': 'application/json'})
    if response.status_code == 200:
        data = response.json()
        return data.get("session_summary", None) if data.get("success") else None
    return None

def store_chat_summary(user_id, history):
    messages = [f"User: {user}\nBot: {bot}" for user, bot in history]
    formatted_conversation = "\n\n".join(messages)
    summary = summarize_chat(formatted_conversation)
    response = requests.post(f'http://{global_ip}/store_chat_summary', json={"user_id": user_id, "session_summary": summary}, headers={'Content-Type': 'application/json'})
    if response.status_code == 200 and response.json().get("success"):
        st.success("Chat summary saved successfully!")
    else:
        st.error("Error in saving chat summary!")

client = OpenAI(api_key="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")

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

def get_relevant_examples(query, max_length=2000):
    examples = []
    total_length = 0
    query_embedding = embedding_model.encode(query)
    conversations_with_scores = []
    for conversation in json_data['Conversations']:
        context_embedding = embedding_model.encode(conversation['Context'])
        similarity = util.cos_sim(query_embedding, context_embedding).item()
        conversations_with_scores.append((conversation, similarity))
    conversations_with_scores.sort(key=lambda x: x[1], reverse=True)
    for conversation, _ in conversations_with_scores:
        example = f"Context: {conversation['Context']}\nResponse: {conversation['Response']}\n\n"
        if total_length + len(example) > max_length:
            break
        examples.append(example)
        total_length += len(example)
    return "".join(examples)

def get_pdf_relevant_examples(query, max_length=2000):
    examples = []
    total_length = 0
    query_embedding = embedding_model.encode(query)
    chunks_with_scores = []
    for chunk, embedding in zip(pdf_chunks, pdf_embeddings):
        similarity = util.cos_sim(query_embedding, embedding).item()
        chunks_with_scores.append((chunk, similarity))
    chunks_with_scores.sort(key=lambda x: x[1], reverse=True)
    for chunk, _ in chunks_with_scores:
        example = f"Except: {chunk}\n\n"
        if total_length + len(example) > max_length:
            break
        examples.append(example)
        total_length += len(example)
    return "".join(examples)

def initialize_session_state(user_id):
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    if 'generated' not in st.session_state:
        st.session_state['generated'] = [f"Hello {user}! I'm here to support your mental health journey. 😊"]
    if 'past' not in st.session_state:
        st.session_state['past'] = [fetch_chat_summary(user_id) or "No previous session data."]

def format_history():
    return "".join([f"User: {u}\nBot: {b}\n\n" for u, b in st.session_state['history']]).strip()

def conversation_chat(question):
    limited_examples = get_relevant_examples(question, max_length=200)
    pdf_examples = get_pdf_relevant_examples(question, max_length=200)
    history = format_history()
    anxiety_web_info = fetch_info_for("anxiety")
    depression_web_info = fetch_info_for("depression")

    prompt = f"""
    The user is seeking culturally sensitive mental health advice.

    Examples:
    {limited_examples}

    Cultural Considerations:
    {pdf_examples}

    History:
    {history}

    Anxiety Info: {anxiety_web_info}
    Depression Info: {depression_web_info}

    User Question: {question}
    """
    response = agent.run(prompt)
    st.session_state['history'].append((question, response))
    return response

def display_chat_history():
    reply_container = st.container()
    container = st.container()
    with container:
        with st.form(key='my_form', clear_on_submit=True):
            user_input = st.text_input("Question:", placeholder="Ask about your mental health", key='input')
            submit_button = st.form_submit_button(label='Send')
        if submit_button and user_input:
            output = conversation_chat(user_input)
            output = str(output) if not isinstance(output, str) else output
            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)
    if st.session_state['generated']:
        with reply_container:
            for i in range(len(st.session_state['generated'])):
                message(st.session_state['past'][i], is_user=True, key=str(i) + '_user', avatar_style="thumbs")
                message(st.session_state['generated'][i], key=str(i), avatar_style="fun-emoji")

initialize_session_state(user_id)
display_chat_history()

if st.button("End Chat Session"):
    store_chat_summary(user_id, st.session_state['history'])
    st.session_state["history"] = []
    st.success(" Chat session ended. Summary saved!")
