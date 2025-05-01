# tools/chat_summary_tool.py
from langchain.tools import BaseTool
from typing import Type, ClassVar
from pydantic import BaseModel, Field
from utils.api_client import APIClient  
import re

class ChatSummaryInput(BaseModel):
    input_str: str = Field(..., description="User ID to fetch personalized chat summary. Example: 'get my chat summary | 1'")

class ChatSummaryTool(BaseTool):
    name: ClassVar[str] = "ChatSummary"
    description: ClassVar[str] = (
        "Use this tool when the user asks about their previous conversations, "
        "chat summaries, or past session details. This tool fetches personalized summaries "
        "from the database based on user_id."
    )
    args_schema: Type[BaseModel] = ChatSummaryInput

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._api_client = APIClient()  
    
    def _run(self, input_str: str) -> str:
        try:
            input_str = input_str.strip()

            # Case 1: input is in correct format like 'query | user_id'
            if "|" in input_str:
                query, user_id = input_str.split("|")
                user_id = int(user_id.strip())
                query = query.strip()

            # Case 2: input is just user_id (e.g. "1")
            elif input_str.isdigit():
                user_id = int(input_str)
                query = "get my chat summary"

            else:
                return "Invalid input format. Provide input as 'your query | user_id'"

            return self._api_client.get_chat_summary(user_id)

        except Exception as e:
            return f"Error while fetching chat summary: {str(e)}"


    async def _arun(self, input_str: str) -> str:
        raise NotImplementedError("Async not supported for ChatSummaryTool.")
