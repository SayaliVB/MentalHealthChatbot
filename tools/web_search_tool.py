# # tools/web_search_tool.py
# from langchain.tools import BaseTool
# from typing import Type, ClassVar
# from pydantic import BaseModel, Field

# # Reusing existing web scraping + search fallback
# from web_search_beautiful import web_search


# class WebSearchInput(BaseModel):
#     query: str = Field(..., description="Query related to mental health, anxiety, depression, stress management etc.")

# class WebSearchTool(BaseTool):
#     name: ClassVar[str] = "WebSearch"
#     description: ClassVar[str] = (
#         "Use this tool to search real-time or current information from trusted websites "
#         "like Mayo Clinic, WebMD, or Healthline. This tool should be used when the user asks about "
#         "latest news, current events, recent research, trending topics, or any general knowledge question "
#         "that is not strictly about mental health stored in the internal database. "
#         "Only use this tool when the user's question requires fresh, real-time, or external information."
#     )
#     args_schema: Type[BaseModel] = WebSearchInput

#     def _run(self, query: str) -> str:
#         """
#         Run the web search.
#         """
#         try:
#             result = web_search(query)
#             if result:
#                 return result
#             else:
#                 return "No relevant information found on trusted health websites."
#         except Exception as e:
#             return f"Error while fetching web data: {str(e)}"

#     async def _arun(self, query: str) -> str:
#         raise NotImplementedError("Async not supported for WebSearchTool.")
# tools/web_search_tool.py

from langchain.tools import BaseTool
from typing import Type, ClassVar
from pydantic import BaseModel, Field

# Import your working web_search function
from web_search_beautiful import web_search

class WebSearchInput(BaseModel):
    query: str = Field(..., description="Search query provided by user.")

class WebSearchTool(BaseTool):
    name: ClassVar[str] = "WebSearch"
    description: ClassVar[str] = (
        "Useful for when you need real-time, current, or general web information. "
        "This tool searches the web using DuckDuckGo and fetches content from the top result. "
        "Use this tool for general knowledge, news, current events, or trending topics "
        "not covered in the internal knowledge base."
    )
    args_schema: Type[BaseModel] = WebSearchInput

    def _run(self, query: str) -> str:
        """
        Perform web search and fetch content.
        """
        try:
            result = web_search(query)
            if result:
                return result
            else:
                return "No relevant information found online."
        except Exception as e:
            return f"Error while fetching web data: {str(e)}"

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("Async not supported for WebSearchTool.")
