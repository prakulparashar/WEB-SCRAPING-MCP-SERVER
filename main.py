import http.client
import json
import os
from fastmcp import FastMCP
import asyncio #mandatory library to use async fxns in python
import httpx #needed when making async api calls, this library basically executes aynschronous https requests
from dotenv import load_dotenv
from utils import clean_html_to_text
load_dotenv()


SERPER_URL = "https://google.serper.dev/search"

mcp = FastMCP("docs")

async def web_search(query:str) -> dict | None:
    payload = json.dumps({"q": query, "num":2})
    headers = {
    'X-API-KEY': os.getenv("SERPER_API_KEY"),
    'Content-Type': 'application/json' # to inform the server that requests will be in json format
    }

    
    async with httpx.AsyncClient() as client:
        response = await client.post(SERPER_URL, headers=headers, data=payload, timeout=30.0)
        response.raise_for_status() #only executes if there is error, otherwise doesn't run 
        return response.json()


#search the req. URL and clean its HTML to get only the text
async def fetch_url(url:str):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, timeout= 30.0)
        cleaned_response = clean_html_to_text(response.text)
        return cleaned_response


#main MCP tool
docs_urls = {
    "langchain": "python.langchain.com/docs",
    "llama-index": "docs.llamaindex.ai/en/stable",
    "openai": "platform.openai.com/docs",
    "uv": "docs.astral.sh/uv",
}



@mcp.tool()
async def get_docs(query:str, library:str):
    """
    Search the latest docs for a given query and library.
    Supports langchain, openai, llama-index and uv.

    Args:
        query: The query to search for (e.g. "Publish a package with UV")
        library: The library to search in (e.g. "uv")

    Returns:
        Summarized text from the docs with source links.
    """
    if library not in docs_urls:
        return "no result found"
    
    query = f"site:{docs_urls[library]} {query}"

    results = await web_search(query)

    if len(results["organic"]) == 0:
        return "no result found"
    
    text_parts = []
    for result in results:
        link = result.get("link", "")

        raw = await fetch_url(link)
        if raw:
            labeled = f"source: {link}/n{raw}" 
            text_parts.append(labeled)

        return "/n/n".join(text_parts)
    

def main():
    mcp.run(transport="stdio")
    

if __name__ == "__main__":
    main()

    
