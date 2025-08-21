import requests
import os
from langchain.tools import BaseTool
from dotenv import load_dotenv

load_dotenv()

from typing import ClassVar
from pydantic import PrivateAttr

class GoogleSearchTool(BaseTool):
    name: ClassVar[str] = "google_search"
    description: ClassVar[str] = "Uses Google Custom Search to find information on the web."
    
    _web_search_tool: 'WebSearchTool' = PrivateAttr()

    def __init__(self, web_search_tool):
        super().__init__()
        self._web_search_tool = web_search_tool

    def _run(self, query: str):
        results = self._web_search_tool.google_search(query)
        return "\n".join(
            f"{item['title']} - {item['link']}"
            for item in results.get("items", [])
        )

    def _arun(self, query: str):
        raise NotImplementedError("No async mode for this tool.")

class WebSearchTool:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.cse_id = os.getenv("GOOGLE_CSE_ID")

    def google_search(self, query, num_results=10):
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.api_key,
            'cx': self.cse_id,
            'q': query,
            'num': num_results
        }
        
        response = requests.get(url, params=params)
        return response.json()
