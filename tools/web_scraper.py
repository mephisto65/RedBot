from typing import ClassVar, Optional
from langchain.tools import BaseTool
import requests
from bs4 import BeautifulSoup
from pydantic import PrivateAttr

class WebScraperTool(BaseTool):
    name: ClassVar[str] = "web_scraper"
    description: ClassVar[str] = (
        "Retrieves and extracts text from HTML web pages only. "
        "DO NOT use this tool for PDF files (.pdf URLs)"
        "This tool is for HTML websites, blogs, articles, and web pages. "
        "Expected input: a URL and an optional CSS selector separated by '||'. "
        "Example: 'https://example.com || p.intro'"
    )

    _session: requests.Session = PrivateAttr(default_factory=requests.Session)

    def _run(self, query: str) -> str:
        try:
            # Parse input: url || css_selector (optional)
            if "||" in query:
                url, selector = map(str.strip, query.split("||", 1))
            else:
                url, selector = query.strip(), None

            response = self._session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            if selector:
                elements = soup.select(selector)
                if not elements:
                    return f"Error: No element found with CSS selector '{selector}'."
                # Concatenate the text of all found elements
                extracted_text = "\n".join(el.get_text(strip=True) for el in elements)
            else:
                # No selector: extract all visible text from the page
                extracted_text = soup.get_text(separator="\n", strip=True)

            return extracted_text[:10000000000] 
        except Exception as e:
            return f"Error during scraping: {str(e)}"

    def _arun(self, query: str):
        raise NotImplementedError("Async mode not supported.")