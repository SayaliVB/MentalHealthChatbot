import os
import json
import requests
import streamlit as st
from streamlit_chat import message
from sentence_transformers import SentenceTransformer, util
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence

# ------------------ CONFIG & ENV ------------------ #
SERPAPI_KEY = "OUR_SERPAPI_KEY_HERE"      #as an example for API search
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Initialize embedding model once
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_text(text):
    return embedding_model.encode(text)

# ------------------ SEARCH USING SERPAPI ------------------ #
def search_web(query, num_results=3):
    """
    Simple example using SerpAPI. It sends the query, 
    gets top results, and returns them as a list of texts.
    """
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": num_results,
    }
    response = requests.get(url, params=params)
    data = response.json()

    results_texts = []
    organic_results = data.get("organic_results", [])
    for result in organic_results:
        # We can combine title + snippet
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        combined = f"{title}\n{snippet}"
        results_texts.append(combined)
    return results_texts

def chunk_text(text, chunk_size=100):
    """Chunk text into smaller segments."""
    words = text.split()
    return [
        " ".join(words[i : i + chunk_size])
        for i in range(0, len(words), chunk_size)
    ]

def retrieve_web_snippets(query, top_k=3):
    """
    1) Search the web via SerpAPI,
    2) chunk each result,
    3) embed and rank to find the top_k relevant chunks.
    """
    # 1) Search
    raw_texts = search_web(query, num_results=5)  # returns list of strings

    # 2) Chunk & embed
    chunked_results = []
    for text in raw_texts:
        for chunk in chunk_text(text):
            chunked_results.append(chunk)

    # 3) Score & rank
    query_embedding = embed_text(query)
    scored_chunks = []
    for chunk in chunked_results:
        chunk_embedding = embed_text(chunk)
        similarity = util.cos_sim(query_embedding, chunk_embedding).item()
        scored_chunks.append((chunk, similarity))

    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    top_snippets = scored_chunks[:top_k]

    # 4) Return as text for prompting
    return "\n\n".join([f"Web Excerpt: {snip[0]}" for snip in top_snippets])

# ------------------ PROMPT & LLM CHAIN ------------------ #
assistant_template = """
You are a compassionate mental health assistant. 
You provide empathetic and actionable advice, considering the user's cultural background as much as possible.

If the user asks for something outside mental health, respond with:
"I can't assist you with that, sorry!"

Relevant cultural data from the web:
{web_data}

Conversation history:
{history}

User's question:
{question}

Give a concise, supportive answer:
"""

prompt = PromptTemplate(
    input_variables=["web_data", "history", "question"],
    template=assistant_template
)

llm = ChatOpenAI(
    temperature=0.6,
    api_key="YOUR_OPENAI_KEY"
)

assistant_chain = prompt | llm

# ------------------ STREAMLIT UI ------------------ #
def init_session_state():
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if "generated" not in st.session_state:
        st.session_state["generated"] = ["Hello! I'm here to support your mental health journey. 😊"]
    if "past" not in st.session_state:
        st.session_state["past"] = ["Hey! 👋"]

def format_history():
    return "\n".join(
        f"User: {user_msg}\nBot: {bot_msg}"
        for user_msg, bot_msg in st.session_state["history"]
    )

def conversation_chat(question):
    # Retrieve from web
    web_data = retrieve_web_snippets(question, top_k=3)
    
    history_str = format_history()

    # Prepare final prompt
    response = assistant_chain.invoke({
        "web_data": web_data,
        "history": history_str,
        "question": question
    })
    answer = response.content if hasattr(response, 'content') else str(response)

    st.session_state["history"].append((question, answer))
    return answer

def main():
    st.title("Multi-Source Mental Health ChatBot 🏥")

    init_session_state()

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Your question:", placeholder="Ask about mental health in different cultures...")
        submit_btn = st.form_submit_button("Send")

    if submit_btn and user_input:
        output = conversation_chat(user_input)
        st.session_state["past"].append(user_input)
        st.session_state["generated"].append(output)

    # Display chat
    for i in range(len(st.session_state["generated"])):
        message(st.session_state["past"][i], is_user=True, key=f"user_{i}")
        message(st.session_state["generated"][i], key=f"bot_{i}")

if __name__ == "__main__":
    main()
