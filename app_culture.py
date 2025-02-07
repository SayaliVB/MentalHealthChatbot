import streamlit as st
from streamlit_chat import message
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os
import json
from sentence_transformers import SentenceTransformer, util
from langchain.schema.runnable import RunnableSequence
from PyPDF2 import PdfReader

os.environ["TOKENIZERS_PARALLELISM"] = "false"

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
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Split text into smaller chunks
def chunk_text(text, chunk_size=500):
    words = text.split()
    chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

# Load and process PDF
pdf_path = 'data/Indian_culture.pdf'
pdf_text = extract_text_from_pdf(pdf_path)
pdf_chunks = chunk_text(pdf_text)

# Compute embeddings for PDF chunks
pdf_embeddings = [embedding_model.encode(chunk) for chunk in pdf_chunks]


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

Cultural background regrading mental health:
{culture}

Here is the conversation history so far:
{history}

Question: {question}
Provide a concise and supportive answer:
"""

# Define the prompt template
assistant_prompt_template = PromptTemplate(
    input_variables=["examples", "culture", "history", "question"],
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

def get_relevant_examples(query, max_length=2000):
    examples = []
    total_length = 0

    # Embed the query
    query_embedding = embedding_model.encode(query)

    # Compute similarity scores for each conversation
    conversations_with_scores = []
    for conversation in json_data['Conversations']:
        context_embedding = embedding_model.encode(conversation['Context'])
        similarity = util.cos_sim(query_embedding, context_embedding).item()
        conversations_with_scores.append((conversation, similarity))

    # Sort by relevance (highest similarity first)
    conversations_with_scores.sort(key=lambda x: x[1], reverse=True)

    for conversation, _ in conversations_with_scores:
        example = f"Context: {conversation['Context']}\nResponse: {conversation['Response']}\n\n"
        example_length = len(example)

        # Check if adding the example exceeds the maximum length
        if total_length + example_length > max_length:
            break

        examples.append(example)
        total_length += example_length

    return "".join(examples)

def get_pdf_relevant_examples(query, max_length=2000):
    examples = []
    total_length = 0

    # Embed the query
    query_embedding = embedding_model.encode(query)

    # Compute similarity scores for each chunk
    chunks_with_scores = []
    for chunk, embedding in zip(pdf_chunks, pdf_embeddings):
        similarity = util.cos_sim(query_embedding, embedding).item()
        chunks_with_scores.append((chunk, similarity))

    # Sort by relevance (highest similarity first)
    chunks_with_scores.sort(key=lambda x: x[1], reverse=True)

    for chunk, _ in chunks_with_scores:
        example = f"Excerpt: {chunk}\n\n"
        example_length = len(example)

        # Check if adding the example exceeds the maximum length
        if total_length + example_length > max_length:
            break

        examples.append(example)
        total_length += example_length

    return "".join(examples)

def initialize_session_state():
    if 'history' not in st.session_state:
        st.session_state['history'] = []

    if 'generated' not in st.session_state:
        st.session_state['generated'] = ["Hello! I'm here to support your mental health journey. 😊"]

    if 'past' not in st.session_state:
        st.session_state['past'] = ["Hey! 👋"]


def format_history():
    """
    Format the chat history into a string for the LLM prompt.
    """
    formatted = ""
    for user_message, bot_response in st.session_state['history']:
        formatted += f"User: {user_message}\nBot: {bot_response}\n\n"
    return formatted.strip()

def conversation_chat(question):
    limited_examples = get_relevant_examples(question, max_length=50)
    pdf_examples = get_pdf_relevant_examples(question, max_length=50)
    history = format_history()
    response = llm_chain.invoke({
        "examples": limited_examples,
        "culture": pdf_examples,
        "history": history,
        "question": question
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
initialize_session_state()
# Display chat history
display_chat_history()
