# utils/memory_manager.py

from langchain.memory import ConversationBufferMemory


def get_memory():
    """
    Initialize and return LangChain Conversation Memory.
    Stores previous user messages for maintaining context.
    """
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,  # Required for agent-based conversation flow
    )
    return memory
