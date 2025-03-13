from http import client
import psycopg2
import requests
import streamlit as st
from streamlit_chat import message
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os
import json
import pinecone
from langchain_community.embeddings import OpenAIEmbeddings
from PyPDF2 import PdfReader
from web_search_beautiful import fetch_info_for
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
import time

os.environ["TOKENIZERS_PARALLELISM"] = "false"

query_params = st.query_params
# st.warning(query_params)
user = query_params.get("user", "Guest")  # Default to "Guest" if not found
user_id = query_params.get("userid", 0)
# st.warning(user)

#  API Configuration
OPENAI_API_KEY = "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"  # Replace with your OpenAI Key
PINECONE_API_KEY = "pcsk_3xjXUT_3Y9ygariTmZbeBDXD7YBQMoMqjbsDRrGDAx4yyCmaEgNjg3Qd1XurMix4wPvRUf"  # Replace with your Pinecone Key
PINECONE_INDEX_NAME = "botonlypdfonestwo"

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


#  Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
# Get the list of all indexes
existing_indexes = pc.list_indexes().names()
print(f"Existing Pinecone Indexes: {existing_indexes}")

if PINECONE_INDEX_NAME in existing_indexes:
    index_info = pc.describe_index(PINECONE_INDEX_NAME)
    if index_info.dimension != 1536:
        print(f"⚠️ Pinecone Index Dimension Mismatch! Expected 1536 but found {index_info.dimension}.")
        print("Deleting index and recreating...")
        pc.delete_index(PINECONE_INDEX_NAME)
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=1536,  # OpenAI embedding size
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
else:
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=1536,  # OpenAI embedding size
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )


#  Connect to Pinecone index
index = pc.Index(PINECONE_INDEX_NAME)

#  Use OpenAI's text-embedding-ada-002 model (1536 dimensions)
embed_model = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=OPENAI_API_KEY)

#  Load JSON dataset
def load_json_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

json_data = load_json_data('data/json_dataset.json')

#  Extract Text from PDF
def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

#  Split PDF Text into Chunks
def chunk_text(text, chunk_size=500):
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

#  Load and Process PDF
pdf_path = 'data/Indian_culture.pdf'
pdf_text = extract_text_from_pdf(pdf_path)
pdf_chunks = chunk_text(pdf_text)

#  Store PDF & JSON Embeddings in Pinecone (Uses OpenAI Embeddings)
def store_embeddings():
    # Store PDF Chunks
    for i, chunk in enumerate(pdf_chunks):
        vector = embed_model.embed_query(chunk)  #  Now using OpenAI embeddings
        index.upsert(vectors=[(f"pdf_{i}", vector, {"text": chunk, "source": "pdf"})])

    # Store JSON Conversations
    for i, conversation in enumerate(json_data["Conversations"]):
        vector = embed_model.embed_query(conversation["Context"])  # ✅ Now using OpenAI embeddings
        index.upsert(vectors=[(f"json_{i}", vector, {"text": conversation["Context"], "source": "json"})])
#  Check if the index already exists in Pinecone

if PINECONE_INDEX_NAME not in existing_indexes:
     with st.spinner("Storing embeddings in Pinecone..."):
        store_embeddings()
        st.success(f"✅ Embeddings successfully stored in index '{PINECONE_INDEX_NAME}'!")
   


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

Also, here is some related info about anxiety:
{anxiety_web_info}

Also, here is some related info about depression:
{depression_web_info}

Question: {question}
Provide a concise and supportive answer:
"""

# Define the prompt template
assistant_prompt_template = PromptTemplate(
    input_variables=["examples", "history","anxiety_web_info","depression_web_info", "question"],
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

# Streamlit UI
st.title("Mental Health ChatBot 🤗")

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


def get_relevant_examples(query, max_length=2000):
    query_embedding = embed_model.embed_query(query)
    results = index.query(vector=query_embedding, top_k=5, include_metadata=True)
    
    examples = []
    total_length = 0
    for match in results["matches"]:
        chunk_text = match["metadata"]["text"]
        example_length = len(chunk_text)

        if total_length + example_length > max_length:
            break

        examples.append(chunk_text)
        total_length += example_length

    return "\n\n".join(examples)

def initialize_session_state(user_id):
    if 'history' not in st.session_state:
        st.session_state['history'] = []

    if 'generated' not in st.session_state:
        st.session_state['generated'] = [f"Hello {user}! I'm here to support your mental health journey. 😊"]

    if 'past' not in st.session_state:
        st.session_state["past"] = [fetch_chat_summary(user_id) or "No previous session data."]


def format_history():
    """
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
    formatted = ""
    for user_message, bot_response in st.session_state['history']:
        formatted += f"User: {user_message}\nBot: {bot_response}\n\n"
    return formatted.strip()

def conversation_chat(question):
    limited_examples = get_relevant_examples(question, max_length=50)
    # pdf_examples = get_pdf_relevant_examples(question, max_length=50)
    history = format_history()
    
    # if not limited_examples and not pdf_examples:
    anxiety_web_info = fetch_info_for("anxiety")  # Call web search function if no relevant data
    depression_web_info = fetch_info_for("depression")  # Call web search function if no relevant data
    # else:
    #     web_info = ""
    
    st.warning(anxiety_web_info)
    st.warning(depression_web_info)

    response = llm_chain.invoke({
        "examples": limited_examples,
        # "culture": pdf_examples,
        "history": history,
        "question": question,
        "anxiety_web_info": anxiety_web_info,
        "depression_web_info": depression_web_info  
    })
    
    if hasattr(response, 'content'):
        response = response.content
    
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
            if not isinstance(output, str):
                output = str(output)

            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)

    if st.session_state['generated']:
        with reply_container:
            for i in range(len(st.session_state['generated'])):
                message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="thumbs")
                message(st.session_state["generated"][i], key=str(i), avatar_style="fun-emoji")

# Initialize session state
initialize_session_state(user_id)
# Display chat history
display_chat_history()

# Save chat summary when user ends session
if st.button("End Chat Session"):
    store_chat_summary(user_id, st.session_state['history'])
    st.session_state["history"] = []  # Clear chat history for new session
    st.success("📝 Chat session ended. Summary saved!")