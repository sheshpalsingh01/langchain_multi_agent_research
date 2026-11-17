import os
from langchain.tools import tool
from requests import request
from dotenv import load_dotenv
from rich import print

from bs4 import BeautifulSoup
from readability import Document
import trafilatura,re
import requests

load_dotenv()
from tavily import TavilyClient

# Load the api keys
tavily_api_key = os.getenv("TAVILY_API_KEY")

tavily = TavilyClient(api_key = tavily_api_key)


# Websearc tool
@tool
def websearch_tool(query:str)->str:
    """
    Search the web for the recent and reliable informmation on the topic, returns titles, url and the content
    """
    
    result = tavily.search(query=query, max_results=4)
    
    out = []
    
    for content in result['results']:
        out.append(
            f"title:{content['title']}\nURL : {content['url']}\nSnippet : {content['content'][:300]}\n"
        )
    
    return "\n------\n".join(out)


# output = websearch_tool("what is current ai news ?")
# print(output)

# Second tool for the agent


@tool(return_direct=True)
def scrape_url(url: str) -> str:
    """
    Scrape and extract clean readable content from a URL.
    Uses multiple extraction strategies for better reliability.
    """

    print(f"[reader] Fetching source: {url}", flush=True)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }

    try:
        # ── Fetch page ─────────────────────────────────────
        response = requests.get(
            url,
            headers=headers,
            timeout=(5, 15)
        )

        response.raise_for_status()

        print("[reader] Download complete; extracting article text.", flush=True)
        html = response.text

        # ──────────────────────────────────────────────────
        # Strategy 1 → trafilatura (BEST for articles/blogs)
        # ──────────────────────────────────────────────────
        extracted = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=False
        )

        if extracted and len(extracted.strip()) > 200:
            cleaned = re.sub(r'\s+', ' ', extracted)
            return cleaned[:5000]

        # ──────────────────────────────────────────────────
        # Strategy 2 → readability
        # ──────────────────────────────────────────────────
        doc = Document(html)
        clean_html = doc.summary()

        soup = BeautifulSoup(clean_html, "html.parser")

        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "form"
        ]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        if text and len(text.strip()) > 200:
            cleaned = re.sub(r'\s+', ' ', text)
            return cleaned[:5000]

        # ──────────────────────────────────────────────────
        # Strategy 3 → fallback full page extraction
        # ──────────────────────────────────────────────────
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "form"
        ]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        cleaned = re.sub(r'\s+', ' ', text)

        if cleaned:
            return cleaned[:5000]

        return "Could not extract meaningful content from the page."

    except requests.exceptions.Timeout:
        return "Request timed out while scraping the URL."

    except requests.exceptions.HTTPError as e:
        return f"HTTP error occurred: {str(e)}"

    except Exception as e:
        return f"Could not scrape URL: {str(e)}"
    

# output2 = scrape_url("https://www.nbcnews.com/artificial-intelligence")
# print(output2)