import os
import json
import faiss
import pickle
import numpy as np
import requests
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
import streamlit as st
from streamlit_chat import message
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from openai import OpenAI

# === Setup ===
os.environ["TOKENIZERS_PARALLELISM"] = "false"
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
dimension = 384

query_params = st.query_params
user = query_params.get("user", "Guest")
user_id = query_params.get("userid", 0)

# === FAISS Indexes and Metadata ===
faiss_pdf_index = faiss.IndexFlatL2(dimension)
faiss_json_index = faiss.IndexFlatL2(dimension)
faiss_web_index = faiss.IndexFlatL2(dimension)

pdf_metadata, json_metadata, web_metadata = [], [], []

def chunk_text(text, chunk_size=500):
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

def store_pdf_embeddings(pdf_path):
    global pdf_metadata, faiss_pdf_index
    if os.path.exists("faiss_pdf.index") and os.path.exists("pdf_metadata.pkl"):
        faiss_pdf_index = faiss.read_index("faiss_pdf.index")
        with open("pdf_metadata.pkl", "rb") as f:
            pdf_metadata = pickle.load(f)
        return
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text)
    vectors = [embedding_model.encode(chunk) for chunk in chunks]
    faiss_pdf_index.add(np.array(vectors).astype("float32"))
    pdf_metadata = [{"text": chunk, "source": "pdf"} for chunk in chunks]
    faiss.write_index(faiss_pdf_index, "faiss_pdf.index")
    with open("pdf_metadata.pkl", "wb") as f:
        pickle.dump(pdf_metadata, f)

def store_json_embeddings(json_path):
    global json_metadata, faiss_json_index
    if os.path.exists("faiss_json.index") and os.path.exists("json_metadata.pkl"):
        faiss_json_index = faiss.read_index("faiss_json.index")
        with open("json_metadata.pkl", "rb") as f:
            json_metadata = pickle.load(f)
        return
    with open(json_path, 'r') as f:
        data = json.load(f)
        for conv in data["Conversations"]:
            vector = embedding_model.encode(conv["Context"])
            faiss_json_index.add(np.array([vector]).astype("float32"))
            json_metadata.append({"text": conv["Context"], "source": "json"})
    faiss.write_index(faiss_json_index, "faiss_json.index")
    with open("json_metadata.pkl", "wb") as f:
        pickle.dump(json_metadata, f)

def scrape_website_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

def store_web_embeddings(urls):
    global web_metadata, faiss_web_index
    if os.path.exists("faiss_web.index") and os.path.exists("web_metadata.pkl"):
        faiss_web_index = faiss.read_index("faiss_web.index")
        with open("web_metadata.pkl", "rb") as f:
            web_metadata = pickle.load(f)
        return
    for url in urls:
        try:
            text = scrape_website_text(url)
            chunks = chunk_text(text)
            for chunk in chunks:
                vector = embedding_model.encode(chunk)
                faiss_web_index.add(np.array([vector]).astype("float32"))
                web_metadata.append({"text": chunk, "url": url})
        except Exception as e:
            print(f"Error processing {url}: {e}")
    faiss.write_index(faiss_web_index, "faiss_web.index")
    with open("web_metadata.pkl", "wb") as f:
        pickle.dump(web_metadata, f)

def query_faiss(index, metadata, query, k=5):
    vector = embedding_model.encode(query).astype("float32").reshape(1, -1)
    _, idxs = index.search(vector, k)
    return [metadata[i] for i in idxs[0]]

def get_relevant_examples(query, max_length=2000, top_k=5):
    results = query_faiss(faiss_pdf_index, pdf_metadata, query, top_k)
    results += query_faiss(faiss_json_index, json_metadata, query, top_k)
    results += query_faiss(faiss_web_index, web_metadata, query, top_k)
    examples = []
    total = 0
    for r in results:
        text = r["text"]
        if total + len(text) > max_length:
            break
        examples.append(text)
        total += len(text)
    return "\n\n".join(examples)

# === Prompt & LLM ===
assistant_template = """
You are a compassionate mental health assistant. Your goal is to help users with empathetic and actionable advice.
Base your answers on the example conversations provided and ensure your responses are concise, clear, and supportive.
Give them some helpful advices, exercises, ways that can help reduce their problems.
You also need to understand the culture of the individual you are talking to. For instance if the person is Indian,
you should take into consideration the stigmas, and other things for advising them.
You do not provide information outside of mental health-related topics. If the question is not relevant, respond with:
"I can't assist you with that, sorry!"

Here are some example conversations:
{examples}

Here is the conversation history so far:
{history}

Question: {question}
Provide a concise and supportive answer:
"""

assistant_prompt_template = PromptTemplate(
    input_variables=["examples", "history", "question"],
    template=assistant_template
)

llm = ChatOpenAI(
    temperature=0.6,
    api_key="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"
)

llm_chain = assistant_prompt_template | llm

# === OpenAI client ===
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

def fetch_chat_summary(user_id):
    response = requests.post(f'http://127.0.0.1:5000/get_chat_summary', json={"user_id": user_id})
    if response.status_code == 200:
        data = response.json()
        return data.get("session_summary") if data.get("success") else None
    return None

def store_chat_summary(user_id, history):
    messages = [f"User: {user}\nBot: {bot}" for user, bot in history]
    summary = summarize_chat("\n\n".join(messages))
    response = requests.post(f'http://127.0.0.1:5000/store_chat_summary', json={"user_id": user_id, "session_summary": summary})
    if response.status_code == 200 and response.json().get("success"):
        st.success("✅ Chat summary saved successfully!")
    else:
        st.error("❌ Failed to save summary.")

def initialize_session_state(user_id):
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    if 'generated' not in st.session_state:
        st.session_state['generated'] = [f"Hello {user}! I'm here to support your mental health journey. 😊"]
    if 'past' not in st.session_state:
        st.session_state['past'] = [fetch_chat_summary(user_id) or "No previous session data."]

def format_history():
    return "\n\n".join([f"User: {u}\nBot: {b}" for u, b in st.session_state['history']])

def conversation_chat(question):
    examples = get_relevant_examples(question)
    history = format_history()
    response = llm_chain.invoke({"examples": examples, "history": history, "question": question})
    if hasattr(response, 'content'):
        response = response.content
    st.session_state['history'].append((question, response))
    return response

def display_chat():
    reply_container = st.container()
    container = st.container()
    with container:
        with st.form(key='chat_form', clear_on_submit=True):
            user_input = st.text_input("Question:", placeholder="Ask about your mental health", key='input')
            submit_button = st.form_submit_button(label='Send')
        if submit_button and user_input:
            output = conversation_chat(user_input)
            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)
    if st.session_state['generated']:
        with reply_container:
            for i in range(len(st.session_state['generated'])):
                message(st.session_state['past'][i], is_user=True, key=f"{i}_user", avatar_style="thumbs")
                message(st.session_state['generated'][i], key=f"{i}", avatar_style="fun-emoji")

# === Run Streamlit App ===
st.title("Mental Health ChatBot 🤗")
store_pdf_embeddings("data/Indian_culture.pdf")
store_json_embeddings("data/json_dataset.json")
store_web_embeddings([
    "https://www.nimh.nih.gov/health/topics/anxiety-disorders",
    "https://www.verywellmind.com/depression-4157287",
    "https://www.who.int/news-room/fact-sheets/detail/mental-health-strengthening-our-response"
])
initialize_session_state(user_id)
display_chat()

if st.button("End Chat Session"):
    store_chat_summary(user_id, st.session_state['history'])
    st.session_state['history'] = []
    st.success("📝 Chat session ended. Summary saved!")