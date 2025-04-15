from http import client
from bs4 import BeautifulSoup
import requests
import streamlit as st
from streamlit_chat import message
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os
import json
from langchain_community.embeddings import OpenAIEmbeddings
from PyPDF2 import PdfReader
from web_search_beautiful import web_search
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from gtts import gTTS
import tempfile
import base64
from agents.router_agent import get_router_agent

# === crisis detection #===
from transformers import pipeline

# === Load suicidal-bert classifier ===
crisis_classifier = pipeline("text-classification", model="gohjiayi/suicidal-bert")

# === Setup ===
os.environ["TOKENIZERS_PARALLELISM"] = "false"
query_params = st.query_params
# st.warning(query_params)
user = query_params.get("user", "Guest")  
user_id = query_params.get("userid", 0)
#  API Configuration
OPENAI_API_KEY = "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" 
PINECONE_API_KEY = "pcsk_3xjXUT_3Y9ygariTmZbeBDXD7YBQMoMqjbsDRrGDAx4yyCmaEgNjg3Qd1XurMix4wPvRUf"  
PINECONE_INDEX_NAME = "botonlypdfonestwo"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
#  Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# === INIT MODELS ===
embed_model = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)

# === INDEX NAMES ===
PDF_INDEX_NAME = "pdf-index"
JSON_INDEX_NAME = "json-index"
WEB_INDEX_NAME = "webdata-index"

# === TEXT SPLITTER ===
def chunk_text(text, chunk_size=500):
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

# === LOAD & STORE PDF DATA ===
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

def store_pdf_embeddings(pdf_path):
    pdf_text = extract_text_from_pdf(pdf_path)
    pdf_chunks = chunk_text(pdf_text)
    for i, chunk in enumerate(pdf_chunks):
        vector = embed_model.embed_query(chunk)
        pdf_index.upsert([(f"pdf_{i}", vector, {"text": chunk, "source": "pdf"})])
    

# === LOAD & STORE JSON DATA ===
def load_json_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def store_json_embeddings(json_path, batch_size=50):
    data = load_json_data(json_path)
    vectors = []
    for i, conversation in enumerate(data["Conversations"]):
        text = conversation["Context"]
        vector = embed_model.embed_query(text)
        vectors.append((f"json_{i}", vector, {"text": text, "source": "json"}))
        # Upload in batches
        if len(vectors) == batch_size:
            json_index.upsert(vectors)
            vectors = []
    # Upload any remaining
    if vectors:
        json_index.upsert(vectors)

    
# === SCRAPE & STORE WEB DATA ===
def scrape_website_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

def store_web_embeddings(urls):
    for site_num, url in enumerate(urls):
        try:
            text = scrape_website_text(url)
            chunks = chunk_text(text)
            for i, chunk in enumerate(chunks):
                vector = embed_model.embed_query(chunk)
                web_index.upsert([(f"web_{site_num}_{i}", vector, {"text": chunk, "url": url})])            
        except Exception as e:
            print(f"❌ Failed to process {url}: {e}")

# === COMBINED RETRIEVAL FUNCTION ===
# def get_relevant_examples(query, max_length=2000, top_k=5):
#     query_embedding = embed_model.embed_query(query)
#     # Query all three indexes
#     results_pdf = pdf_index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
#     results_json = json_index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
#     results_web = web_index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
#     # Combine and sort
#     combined = results_pdf["matches"] + results_json["matches"] + results_web["matches"]
#     combined.sort(key=lambda x: x["score"], reverse=True)
#     examples = []    
#     total_length = 0
#     for match in combined:
#         chunk_text = match["metadata"]["text"]
#         source = match["metadata"].get("url") or match["metadata"].get("source", "unknown")
#         if total_length + len(chunk_text) > max_length:
#             break
#         examples.append(chunk_text)       
#         total_length += len(chunk_text)
#     return "\n\n".join(examples)

# ################# pincecone_search ##########################
# def pinecone_search(query: str) -> str:
#     return get_relevant_examples(query)

################# tts ##########################
def play_tts(text):
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tts.save(tmp_file.name)
        audio_path = tmp_file.name

    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
        b64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
        <audio autoplay controls>
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

###############################################
# ======= CRISIS DETECTION =========== #
def gpt_crisis_check(user_input: str) -> bool:
    prompt = f"""
    You are a safety classifier. Determine if this message indicates that the user may be in crisis, having suicidal thoughts, or expressing harmful or violent intent toward others. 
    Consider if the user expresses any intent to harm others or themselves in any form, including but not limited to violence, aggression, or threats.

    Message: "{user_input}"

    Answer "Yes" if it indicates suicidal thoughts, aggression, harm toward others, or harmful intent, otherwise answer "No".
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=5,
        temperature=0
    )

    answer = response.choices[0].message.content.strip().lower()
    return "yes" in answer


def is_crisis(user_input: str, threshold: float = 0.5) -> bool:
    # 1. Classifier
    result = crisis_classifier(user_input)[0]
    label = result['label']
    score = result['score']

    # 2. Keyword override
    suicide_keywords = [
        "end my life", "kill myself", "no reason to live", "want to die",
        "suicidal", "give up", "commit suicide", "i'm done with everything"
    ]
    keyword_match = any(kw in user_input.lower() for kw in suicide_keywords)

    # 3. GPT fallback
    gpt_thinks_crisis = gpt_crisis_check(user_input)

    # Final result
    crisis = (label == 'LABEL_1' and score >= threshold) or keyword_match or gpt_thinks_crisis

    # Debug logging
    st.sidebar.markdown(f"**[DEBUG] Suicidal BERT:** `{label}` with score `{score:.2f}`")
    st.sidebar.markdown(f"**[DEBUG] Keywords triggered:** `{keyword_match}`")
    st.sidebar.markdown(f"**[DEBUG] GPT says crisis:** `{gpt_thinks_crisis}`")
    st.sidebar.markdown(f"**[DEBUG] FINAL DECISION:** `{crisis}`")
    return crisis

# === Predefined safe response ===
def crisis_tool_response():
    return (
        "Crisis detected "
        "Please reach out to a mental health professional or call a crisis helpline in your area. "
        "You're valuable and deserve support. "
    )

# === Main decision function for handling messages ===
def agent_or_crisis_chat(user_input):
    if is_crisis(user_input):
        response = crisis_tool_response()
        print(response)
    else:
        response = conversation_chat(user_input)  # This is your original LangChain or LLM-based function
    st.session_state['history'].append((user_input, response))
    return response


# Prepare the template
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
Here is the conversation history so far:
{history}
Question: {question}
Provide a concise and supportive answer:
"""
# Define the prompt template
assistant_prompt_template = PromptTemplate(
    input_variables=["examples", "history", "question"],
    template=assistant_template
)

# Define the local LLM
llm = ChatOpenAI(
    # base_url="http://localhost:1234/v1",
    temperature=0.6,
    api_key="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"
)

# Create an LLM chain
llm_chain = assistant_prompt_template | llm
global_ip='127.0.0.1:5000'

# Function to fetch past chat summary
def fetch_chat_summary(user_id):
    response = requests.post(f'http://{global_ip}/get_chat_summary', json={"user_id": user_id}, headers={'Content-Type': 'application/json'})
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            return data.get("session_summary", None)
        else:
            return None
    else:
        return None

# Function to store chat summary in PostgreSQL
def store_chat_summary(user_id, history):
    # Convert chat history (list of tuples) into readable text format
    messages = [f"User: {user}\nBot: {bot}" for user, bot in history]  # Formats chat history
    formatted_conversation = "\n\n".join(messages)  # Joins messages into a single string
    summary = summarize_chat(formatted_conversation)
    response = requests.post(f'http://{global_ip}/store_chat_summary', json={"user_id": user_id, "session_summary": summary}, headers={'Content-Type': 'application/json'})
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            st.success("✅ Chat summary saved successfully!")
    else:
        st.success(" Error in saving chat summary!")


# Initialize OpenAI client
client = OpenAI(api_key="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")
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

def initialize_session_state(user_id):
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    if 'generated' not in st.session_state:
        st.session_state['generated'] = [f"Hello {user}! I'm here to support your mental health journey. 😊"]
    if 'past' not in st.session_state:
        st.session_state["past"] = [fetch_chat_summary(user_id) or "No previous session data."]
    if "last_spoken_index" not in st.session_state:
        st.session_state["last_spoken_index"] = -1

def format_history():   
    formatted = ""
    # Add past conversation summary (always at index 0)
    if "past" in st.session_state and len(st.session_state["past"]) > 0:
        formatted += f"Previous Conversations Summary:\n{st.session_state['past'][0]}\n\n"
    # Add current session history
    formatted += "Current Session:\n"
    for user_message, bot_response in st.session_state['history']:
        formatted += f"User: {user_message}\nBot: {bot_response}\n\n"
    return formatted.strip()
    """
    do not remove this text
    formatted = ""
    for user_message, bot_response in st.session_state['history']:
        formatted += f"User: {user_message}\nBot: {bot_response}\n\n"
    return formatted.strip()
    """
def conversation_chat(user_input: str) -> str:
    try:
        response = router_agent.run(user_input)
        print("conversation_chat", response)
        if hasattr(response, 'content'):  # just in case (usually not needed)
            response = response.content

        # Track chat history in session
        st.session_state['history'].append((user_input, response))
        return response

    except Exception as e:
        error_msg = f"⚠️ Sorry, something went wrong: {str(e)}"
        st.session_state['history'].append((user_input, error_msg))
        return error_msg 

def display_chat_history():
    reply_container = st.container()
    container = st.container()
    with container:
        with st.form(key='my_form', clear_on_submit=True):
            user_input = st.text_input("Question:", placeholder="Ask about your mental health", key='input')
            submit_button = st.form_submit_button(label='Send')
        if submit_button and user_input:
            output = agent_or_crisis_chat(user_input)
            if not isinstance(output, str):
                output = str(output)
            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)    
    if st.session_state['generated']:
        with reply_container:
            for i in range(len(st.session_state['generated'])):
                message(st.session_state["past"][i], is_user=True, key=f"{i}_user", avatar_style="thumbs")
                message(st.session_state["generated"][i], key=f"{i}", avatar_style="fun-emoji")
                 # 🔊 Speak the last generated message only once
                if tts_enabled and i == len(st.session_state['generated']) - 1 and i > st.session_state["last_spoken_index"]:
                    play_tts(st.session_state["generated"][i])
                    st.session_state["last_spoken_index"] = i

# Run Streamlit UI
st.title("Mental Health ChatBot 🤗")
tts_enabled = st.checkbox("🔊 Enable Text-to-Speech (TTS)", value=True)

# === Get all existing indexes from Pinecone ===
existing_indexes = pc.list_indexes().names()

# === Create and store embeddings only if index doesn't exist ===
if PDF_INDEX_NAME not in existing_indexes:
    pc.create_index(
        name=PDF_INDEX_NAME,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    pdf_index = pc.Index(PDF_INDEX_NAME)
    store_pdf_embeddings("data/Indian_culture.pdf")
else:
    pdf_index = pc.Index(PDF_INDEX_NAME)

if JSON_INDEX_NAME not in existing_indexes:
    pc.create_index(
        name=JSON_INDEX_NAME,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    json_index = pc.Index(JSON_INDEX_NAME)
    store_json_embeddings("data/json_dataset.json")
else:
    json_index = pc.Index(JSON_INDEX_NAME)

if WEB_INDEX_NAME not in existing_indexes:
    pc.create_index(
        name=WEB_INDEX_NAME,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    web_index = pc.Index(WEB_INDEX_NAME)
    store_web_embeddings([
        "https://www.nimh.nih.gov/health/topics/anxiety-disorders",
        "https://www.verywellmind.com/depression-4157287",
        "https://www.who.int/news-room/fact-sheets/detail/mental-health-strengthening-our-response"
    ])
else:
    web_index = pc.Index(WEB_INDEX_NAME)

router_agent = get_router_agent(
    embed_model=embed_model,
    pdf_index=pdf_index,
    json_index=json_index,
    web_index=web_index
)

# Initialize session state
initialize_session_state(user_id)
# Display chat history
display_chat_history()

# Save chat summary when user ends session
if st.button("End Chat Session"):
    store_chat_summary(user_id, st.session_state['history'])
    st.session_state["history"] = []  # Clear chat history for new session
    st.success("📝 Chat session ended. Summary saved!")