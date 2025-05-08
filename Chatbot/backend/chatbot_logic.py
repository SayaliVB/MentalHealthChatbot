# chatbot_logic.py
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
from langchain.schema import AIMessage, HumanMessage

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

# === Utilities ===
def load_json_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())

# === Crisis Detection ===
def gpt_crisis_check(user_input: str) -> bool:
    prompt = f"""
    You are a crisis safety classifier.
    ONLY answer "Yes" if the user explicitly expresses suicidal thoughts, self-harm intentions, or talks about ending their life.
    Ignore expressions of general sadness, anxiety, coping, or stress unless suicide/self-harm is clearly mentioned.
    
    Message: "{user_input}"

    Answer exactly "Yes" or "No".
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}],
        max_tokens=5,
        temperature=0
    )
    answer = response.choices[0].message.content.strip().lower()
    return "yes" in answer

def is_crisis(user_input: str, threshold: float = 0.7) -> bool:
    result = crisis_classifier(user_input)[0]
    label = result['label']
    score = result['score']

    suicide_keywords = [
        "end my life", "kill myself", "no reason to live", "want to die",
        "suicidal", "give up", "commit suicide", "i'm done with everything"
    ]

    keyword_match = any(kw in user_input.lower() for kw in suicide_keywords)
    gpt_check = gpt_crisis_check(user_input)

    if keyword_match:
        return True
    if (label == 'LABEL_1' and score >= threshold) and gpt_check:
        return True

    return False

def crisis_tool_response():
    return (
         
        "Help is available<br>"
        "988 Suicide and Crisis Lifeline<br>"
        "Call or SMS:<br>"
        "988<br>"
        'Chat: <a href="https://chat.988lifeline.org" target="_blank" rel="noopener noreferrer">'
        "https://chat.988lifeline.org</a>"
    )
    
    "\u26a0\ufe0f Crisis detected. Please reach out to a mental health professional or call a crisis helpline in your area. "
    "You're valuable and deserve support."

# === Chat Summary ===
def create_chat_summary(history):
    messages = [
        f"User: {history[i]['text']}\nBot: {history[i + 1]['text']}"
        for i in range(0, len(history) - 1, 2)
    ]
    formatted_conversation = "\n\n".join(messages)
    summary = summarize_chat(formatted_conversation)
    return summary

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
        return base64.b64encode(audio_bytes).decode()

# === Raw LLM Call ===
def get_raw_llm_response(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful mental health assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"LLM error: {str(e)}"

def rank_responses(query: str, raw_response: str, agent_response: str) -> str:
    """
    Use GPT-4 to evaluate which response is more helpful to the user.
    """
    try:
        comparison_prompt = f"""
        You are evaluating two responses given to the user’s mental health query: "{query}".

        Response A (from the base OpenAI model):
        {raw_response}

        Response B (from a LangChain agent with tool usage):
        {agent_response}

        Which response is more helpful, supportive, and informative for the user? Consider accuracy, empathy, and helpfulness.
        Reply with only "A" or "B".
        """
        comparison = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": comparison_prompt}],
            max_tokens=5,
            temperature=0
        )
        return comparison.choices[0].message.content.strip().upper()
    except Exception as e:
        print(f" Error comparing responses: {e}")
        return "B"  

def get_bot_response(user_input: str, history: list = [], user_name: str = "User", culture: str = "Unknown", user_id: int = None) -> str:
    try:
        if is_crisis(user_input):
            return crisis_tool_response()

        # Rebuild conversation history
        chat_history = []
        for message in history:
            if message['sender'] == 'user':
                chat_history.append(HumanMessage(content=message['text']))
            elif message['sender'] == 'ai':
                chat_history.append(AIMessage(content=message['text']))
        router_agent.memory.chat_memory.messages = chat_history

        CULTURE_PRACTICES = {
            "India": "yoga, meditation, breathing techniques, family support",
            "Japan": "mindfulness, community harmony, resilience practices",
            "USA": "therapy, self-help groups, structured counseling",
            "Mexico": "faith-based support, family gatherings, community closeness",
            "Nigeria": "spirituality, storytelling, extended family support",
            "China": "Tai Chi, meditation, family cohesion",
            "UK": "guided therapy, journaling, CBT techniques",
            "Unknown": "general global stress management techniques"
        }

        practices = CULTURE_PRACTICES.get(culture, CULTURE_PRACTICES["Unknown"])

        system_message = f"""
        You are a culturally aware mental health assistant.

        The user you are helping is from the {culture} culture.
        When suggesting coping strategies for mental health concerns like anxiety, sadness, or stress,
        prioritize including culturally common practices such as: {practices}.

        Also, naturally address the user by their first name, {user_name}, in your responses.
        Your tone should be empathetic, calming, and human-like.
        """

        # === Detect if we should format the input for ChatSummaryTool
        summary_keywords = [
            "summary", "previous", "chat", "conversation", "session",
            "what did we talk", "my summary", "past"
        ]
        if any(kw in user_input.lower() for kw in summary_keywords) and "|" not in user_input and user_id:
            modified_input = f"{user_input.strip()} | {user_id}"
            print("🧠 Modified input for ChatSummaryTool:", modified_input)
        else:
            modified_input = user_input

        # === Raw LLM output
        raw_llm_response = get_raw_llm_response(modified_input)
        print(f"🔍 Raw LLM response: {raw_llm_response}")

        # === Agent toolchain execution
        personalized_agent = get_router_agent(embed_model, pdf_index, json_index, web_index, system_message)
        personalized_agent.memory.chat_memory.messages = chat_history
        agent_result = personalized_agent.invoke(modified_input)
        agent_response = agent_result["output"]

        # === Tool detection (structured logic)
        intermediate = agent_result.get("intermediate_steps", [])
        tool_used = any(
            "Observation:" in step.get("log", "") and "Error" not in step.get("log", "")
            for step in intermediate
        )

        if tool_used:
            print("✅ Tool was used successfully — using agent response.")
            return agent_response
        else:
            print("🧠 No valid tool output — falling back to raw LLM response.")
            selected = rank_responses(modified_input, raw_llm_response, agent_response)
            return agent_response if selected == "B" else raw_llm_response

    except Exception as e:
        return f"Agent Error: {str(e)}"
