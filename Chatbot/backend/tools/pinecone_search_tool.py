# tools/pinecone_search_tool.py
from langchain.tools import BaseTool
from typing import Type, ClassVar
from pydantic import BaseModel, Field

# Import from utils (refactored location)
from utils.pinecone_rag import pinecone_search

class PineconeSearchInput(BaseModel):
    query: str = Field(..., description="Query related to mental health, culture, anxiety, depression, etc.")

class PineconeSearchTool(BaseTool):
    name: ClassVar[str] = "PineconeSearch"
    description: ClassVar[str] = (
        "Use this tool to answer queries related to mental health topics such as anxiety, depression, stress, "
        "coping techniques, therapy advice, cultural factors, and symptoms. This tool searches the internal knowledge "
        "base stored in Pinecone Vector DB which includes curated content from PDFs, JSON datasets, and web scraped sources. "
        "Only use this tool for mental health specific queries."
    )
    
    args_schema: Type[BaseModel] = PineconeSearchInput

    def __init__(self, embed_model, pdf_index, json_index, web_index, **kwargs):
        super().__init__(**kwargs)
        self._embed_model = embed_model
        self._pdf_index = pdf_index
        self._json_index = json_index
        self._web_index = web_index

    def _run(self, query: str) -> str:
        try:
            result = pinecone_search(
                query,
                self._embed_model,
                self._pdf_index,
                self._json_index,
                self._web_index
            )
            if result:
                unique_lines = list(set(result.split("\n")))
                cleaned_result = "\n".join(unique_lines)
                return cleaned_result
            else:
                return "No relevant information found in the knowledge base."
        except Exception as e:
            return f"Error while searching Pinecone DB: {str(e)}"

    async def _arun(self, query: str) -> str:
        raise NotImplementedError("Async not supported for PineconeSearchTool.")
