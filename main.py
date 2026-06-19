import http.client
import json
import os
import asyncio #mandatory library to use async fxns in python
import httpx #needed when making async api calls, this library basically executes aynschronous https requests
from dotenv import load_dotenv
load_dotenv()

query = "chromadb"
SERPER_URL = "https://google.serper.dev/search"

async def web_search(query:str) -> dict | None:
    payload = json.dumps({"q": query, "num":2})
    headers = {
    'X-API-KEY': os.getenv("SERPER_API_KEY"),
    'Content-Type': 'application/json' # to inform the server that requests will be in json format
    }

    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            SERPER_URL, headers=headers, data=payload, timeout=30.0
        )
        response.raise_for_status() #only executes if there is error, otherwise doesn't run 
        return response.json()

res = asyncio.run(web_search(query="Chroma DB"))
print(res)

