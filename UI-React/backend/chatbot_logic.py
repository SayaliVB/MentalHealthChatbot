import os
import json
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer, util
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

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

# Prompt Template
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

assistant_prompt_template = PromptTemplate(
    input_variables=["examples", "culture", "history", "question"],
    template=assistant_template
)

# LLM setup
llm = ChatOpenAI(
    temperature=0.6,
    api_key="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"
)

llm_chain = assistant_prompt_template | llm

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
        example = f"Excerpt: {chunk}\n\n"
        if total_length + len(example) > max_length:
            break
        examples.append(example)
        total_length += len(example)

    return "".join(examples)

def get_bot_response(user_input, history=""):
    examples = get_relevant_examples(user_input, max_length=2000)
    culture = get_pdf_relevant_examples(user_input, max_length=2000)
    response = llm_chain.invoke({
        "examples": examples,
        "culture": culture,
        "history": history,
        "question": user_input
    })
    return response.content if hasattr(response, 'content') else str(response)
