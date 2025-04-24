# agents/router_agent.py
from langchain.agents import initialize_agent, Tool, AgentType
from langchain_community.llms import OpenAI
from utils.memory_manager import get_memory

# Import Tools
from tools.pinecone_search_tool import PineconeSearchTool
from tools.web_search_tool import WebSearchTool
# from tools.sentiment_tool import SentimentAnalysisTool
# from tools.crisis_detection_tool import CrisisDetectionTool
from tools.chat_summary_tool import ChatSummaryTool

import os
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_router_agent(embed_model, pdf_index, json_index, web_index):
    """
    Builds and returns the Router Agent with all registered tools.
    """
    print("inside router_agent")
    print("embed_model", embed_model)
    print("pdf_index", pdf_index)
    print("json_index", json_index)
    print("web_index", web_index)
    llm = OpenAI(
        temperature=0.7,
        openai_api_key=OPENAI_API_KEY
    )

    memory = get_memory()

    tools = [
        PineconeSearchTool(embed_model, pdf_index, json_index, web_index),
        WebSearchTool(),
        ChatSummaryTool(),
    ]

    system_message = """
    You are an intelligent mental health assistant.

    Your job is to carefully analyze user queries and route them to the most appropriate tool.

    Rules for Tool Usage:

    1. Use the 'PineconeSearch' tool when:
    - The user asks about mental health, symptoms, therapy, anxiety, depression, coping strategies, or cultural factors.
    - Keywords may include: "anxiety", "depression", "mental health", "symptoms", "therapy", "treatment", "advice", "stress", "coping", "culture".

    You are a helpful mental health assistant.

    When you use the PineconeSearch tool, DO NOT generate your own answer.
    Instead, simply return the exact output from the PineconeSearch tool to the user — word for word.

    If PineconeSearch returns nothing helpful, respond with a kind, supportive message of your own.

    Use WebSearch for recent events. Use ResourceLookup for chat summaries.

    NEVER override PineconeSearch tool results. Just pass them along directly to the user.
    
    2. Use the 'WebSearch' tool when:
    - The user asks about current events, news, real-time info, recent discoveries, latest updates.
    - Keywords may include: "latest", "current", "new", "today", "2024", "benefits of", "trending", "real-time".

    3. Use the 'ResourceLookup' tool when:
    - The user wants information about their previous sessions or chat summary.
    - Keywords may include: "last chat", "chat summary", "previous conversation", "what did we talk about", "my summary", "past session".

    Rules:
    - Always use ONLY ONE tool per query.
    - Prefer PineconeSearch when in doubt for general mental health queries.
    - Be empathetic, supportive, and concise.
    - Do not invent any data. Always rely on tool output if available.
    """
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True,
        memory=memory,
        handle_parsing_errors=True,
        system_message=system_message
    )

    return agent
