# # chatbot_logic.py
# import os
# import json
# from PyPDF2 import PdfReader
# from sentence_transformers import SentenceTransformer
# from pinecone import Pinecone
# from langchain_openai import OpenAIEmbeddings


# from agents.router_agent import get_router_agent

# # === ENV VARS ===
# os.environ["TOKENIZERS_PARALLELISM"] = "false"
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# # === Load Embedding Model ===
# embed_model = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=OPENAI_API_KEY)

# # === Init Pinecone ===
# pc = Pinecone(api_key=PINECONE_API_KEY)

# # === Vector Indexes ===
# pdf_index = pc.Index("pdf-index")
# json_index = pc.Index("json-index")
# web_index = pc.Index("webdata-index")

# # === Pass everything to Router Agent ===
# router_agent = get_router_agent(
#     embed_model=embed_model,
#     pdf_index=pdf_index,
#     json_index=json_index,
#     web_index=web_index
# )

# # === Load PDF & JSON (Optional if used in tools) ===
# def load_json_data(file_path):
#     with open(file_path, 'r') as f:
#         return json.load(f)

# def extract_text_from_pdf(file_path):
#     reader = PdfReader(file_path)
#     return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

# # (optional) Load for external context tools
# json_data = load_json_data("data/json_dataset.json")
# pdf_text = extract_text_from_pdf("data/Indian_culture.pdf")
# pdf_chunks = [" ".join(pdf_text.split()[i:i+500]) for i in range(0, len(pdf_text.split()), 500)]
# pdf_embeddings = [SentenceTransformer('all-MiniLM-L6-v2').encode(chunk) for chunk in pdf_chunks]

# # === Main Bot Logic ===
# def get_bot_response(user_input: str, history: str = "") -> str:
#     try:
#         result = router_agent.run(user_input)
#         return result if isinstance(result, str) else str(result)
#     except Exception as e:
#         return f"⚠️ Agent Error: {str(e)}"
import os
import json
import tempfile
import base64
from gtts import gTTS
from PyPDF2 import PdfReader
from transformers import pipeline
from openai import OpenAI
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from agents.router_agent import get_router_agent

# === ENV VARS ===
os.environ["TOKENIZERS_PARALLELISM"] = "false"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# === Init Clients ===
embed_model = OpenAIEmbeddings(model="text-embedding-ada-002", openai_api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
client = OpenAI(api_key=OPENAI_API_KEY)
crisis_classifier = pipeline("text-classification", model="gohjiayi/suicidal-bert")

# === Indexes ===
pdf_index = pc.Index("pdf-index")
json_index = pc.Index("json-index")
web_index = pc.Index("webdata-index")

# === Agent ===
router_agent = get_router_agent(embed_model, pdf_index, json_index, web_index)

# === Optional: Load raw data for embedding debug ===
def load_json_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

# === CRISIS DETECTION ===
def gpt_crisis_check(user_input: str) -> bool:
    prompt = f"""
    You are a safety classifier. Determine if this message indicates that the user may be in crisis, having suicidal thoughts, or expressing harmful or violent intent.

    Message: "{user_input}"
    Answer "Yes" if crisis is detected, otherwise "No".
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
    result = crisis_classifier(user_input)[0]
    label = result['label']
    score = result['score']
    suicide_keywords = [
        "end my life", "kill myself", "no reason to live", "want to die",
        "suicidal", "give up", "commit suicide", "i'm done with everything"
    ]
    keyword_match = any(kw in user_input.lower() for kw in suicide_keywords)
    gpt_check = gpt_crisis_check(user_input)
    return (label == 'LABEL_1' and score >= threshold) or keyword_match or gpt_check

def crisis_tool_response():
    return (
        "⚠️ Crisis detected. Please reach out to a mental health professional or call a crisis helpline in your area. "
        "You're valuable and deserve support."
    )

# === Chat Summary ===


# Function to store chat summary in PostgreSQL
def create_chat_summary(history):
    # history = "Chat Hisory Chat History Chat History Chat History"
    # Convert chat history (list of tuples) into readable text format
    messages = [
    f"User: {history[i]['text']}\nBot: {history[i + 1]['text']}"
    for i in range(0, len(history) - 1, 2)]
    
    print(messages)

    formatted_conversation = "\n\n".join(messages)  # Joins messages into a single string
    summary = summarize_chat(formatted_conversation)
    return summary

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



# === TTS Function ===
def play_tts(text):
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
        tts.save(tmp_file.name)
        audio_path = tmp_file.name
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()
        return base64.b64encode(audio_bytes).decode()  # Return base64 audio string

# === Bot Logic ===
def get_bot_response(user_input: str, history: str = "") -> str:
    try:
        if is_crisis(user_input):
            return crisis_tool_response()
        response = router_agent.run(user_input)
        return response if isinstance(response, str) else str(response)
    except Exception as e:
        return f"Agent Error: {str(e)}"
