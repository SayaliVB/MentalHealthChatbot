from http import client
import psycopg2
import requests
import streamlit as st
from streamlit_chat import message
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os
import json
from sentence_transformers import SentenceTransformer, util
from langchain.schema.runnable import RunnableSequence
from PyPDF2 import PdfReader
from web_search_beautiful import fetch_info_for
import openai  # Ensure OpenAI integration for summarization

os.environ["TOKENIZERS_PARALLELISM"] = "false"
OPENAI_API_KEY ="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"



query_params = st.query_params
user = query_params.get("user", "Guest")  
user_id = query_params.get("userid", 0)

# API Base URL
global_ip = '127.0.0.1:5000'

# Load and parse the JSON file
def load_json_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

json_data = load_json_data('data/json_dataset.json')

# Load a pre-trained sentence embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Extract text from a PDF
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    return "".join([page.extract_text() for page in reader.pages])

# Split text into smaller chunks
def chunk_text(text, chunk_size=500):
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

# Load and process PDF
pdf_path = 'data/Indian_culture.pdf'
pdf_text = extract_text_from_pdf(pdf_path)
pdf_chunks = chunk_text(pdf_text)
pdf_embeddings = [embedding_model.encode(chunk) for chunk in pdf_chunks]

# Chatbot Prompt Template
assistant_template = """
You are a compassionate mental health assistant. Your goal is to help users with empathetic and actionable advice. 
Base your answers on the example conversations provided and ensure your responses are concise, clear, and supportive. 
Give them some helpful advices, exercises, ways that can help reduce their problems.
You also need to understand the culture of the individual you are talking to. For instance if the person is Indian, you 
should take into consideration the stigmas, and other things for advising them.
You do not provide information outside of mental health-related topics. If the question is not relevant, respond with: 
"I can't assist you with that, sorry!"

Here are some example conversations:
{examples}

Cultural background regarding mental health:
{culture}

Here is the conversation history so far:
{history}

Also, here is some related info about anxiety:
{anxiety_web_info}

Also, here is some related info about depression:
{depression_web_info}

Question: {question}
Provide a concise and supportive answer:
"""

# Define the prompt template
assistant_prompt_template = PromptTemplate(
    input_variables=["examples", "culture", "history", "anxiety_web_info", "depression_web_info", "question"],
    template=assistant_template
)

# Define the local LLM
llm = ChatOpenAI(
    temperature=0.6,
    api_key ="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"

)

# Create an LLM chain
llm_chain = assistant_prompt_template | llm

# Function to fetch past chat summary
def fetch_chat_summary(user_id):
    response = requests.post(f'http://{global_ip}/get_chat_summary', json={"user_id": user_id}, headers={'Content-Type': 'application/json'})
    if response.status_code == 200:
        data = response.json()
        return data.get("session_summary", None) if data.get("success") else None
    return None

# Function to store chat summary in PostgreSQL
def store_chat_summary(user_id, messages):
    summary = summarize_chat(messages)
    response = requests.post(f'http://{global_ip}/store_chat_summary', json={"user_id": user_id, "session_summary": summary}, headers={'Content-Type': 'application/json'})
    if response.status_code == 200 and response.json().get("success"):
        st.success("✅ Chat summary saved successfully!")
    else:
        st.error("❌ Error in saving chat summary!")

# Function to summarize chat session using GPT
def summarize_chat(messages):
    prompt = f"""
    You are a mental health chatbot that summarizes user conversations in a few sentences. 
    Focus on the user's emotional state, concerns, and key advice given.

    Chat Transcript:
    {messages}

    Provide a concise and human-friendly summary:
    """
    client = openai.OpenAI(api_key=OPENAI_API_KEY)  # Create OpenAI client instance

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=200,
        temperature=0.5
    )
    
    return response.choices[0].message.content.strip()

#  Retrieve relevant examples based on user query
def get_relevant_examples(query, max_length=2000):
    examples = []
    total_length = 0
    query_embedding = embedding_model.encode(query)

    # Compute similarity scores for each conversation
    conversations_with_scores = [(c, util.cos_sim(query_embedding, embedding_model.encode(c['Context'])).item()) for c in json_data['Conversations']]
    conversations_with_scores.sort(key=lambda x: x[1], reverse=True)

    for conversation, _ in conversations_with_scores:
        example = f"Context: {conversation['Context']}\nResponse: {conversation['Response']}\n\n"
        if total_length + len(example) > max_length:
            break
        examples.append(example)
        total_length += len(example)
    return "".join(examples)

# Retrieve relevant PDF examples
def get_pdf_relevant_examples(query, max_length=2000):
    examples = []
    total_length = 0
    query_embedding = embedding_model.encode(query)

    chunks_with_scores = [(chunk, util.cos_sim(query_embedding, embedding).item()) for chunk, embedding in zip(pdf_chunks, pdf_embeddings)]
    chunks_with_scores.sort(key=lambda x: x[1], reverse=True)

    for chunk, _ in chunks_with_scores:
        example = f"Excerpt: {chunk}\n\n"
        if total_length + len(example) > max_length:
            break
        examples.append(example)
        total_length += len(example)
    return "".join(examples)

# Initialize session state
def initialize_session_state(user_id):
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    if 'generated' not in st.session_state:
        st.session_state['generated'] = [f"Hello {user}! I'm here to support your mental health journey. 😊"]
    if 'past' not in st.session_state:
        st.session_state["past"] = [fetch_chat_summary(user_id) or "No previous session data."]

initialize_session_state(user_id)

# Format chat history for LLM prompt
def format_history():
    return "\n".join(f"User: {msg[0]}\nBot: {msg[1]}" for msg in st.session_state['history'])

# Chatbot conversation function
def conversation_chat(question):
    limited_examples = get_relevant_examples(question, max_length=50)
    pdf_examples = get_pdf_relevant_examples(question, max_length=50)
    history = format_history()

    anxiety_info = fetch_info_for("anxiety")
    depression_info = fetch_info_for("depression")

    response = llm_chain.invoke({
        "examples": limited_examples,
        "culture": pdf_examples,
        "history": history,
        "question": question,
        "anxiety_web_info": anxiety_info,
        "depression_web_info": depression_info  
    })
    
    if hasattr(response, 'content'):
        response = response.content

    st.session_state['history'].append((question, response))
    return response

# Display chat history in Streamlit
def display_chat_history():
    reply_container = st.container()
    container = st.container()

    with container:
        with st.form(key='my_form', clear_on_submit=True):
            user_input = st.text_input("Question:", placeholder="Ask about your mental health", key='input')
            submit_button = st.form_submit_button(label='Send')

        if submit_button and user_input:
            output = conversation_chat(user_input)
            if not isinstance(output, str):
                output = str(output)

            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)

    if st.session_state['generated']:
        with reply_container:
            for i in range(len(st.session_state['generated'])):
                message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="thumbs")
                message(st.session_state["generated"][i], key=str(i), avatar_style="fun-emoji")

display_chat_history()

if st.button("End Chat Session"):
    store_chat_summary(user_id, [chat[0] for chat in st.session_state["history"]])
    st.session_state["history"] = []
    st.success("📝 Chat session ended. Summary saved!")
