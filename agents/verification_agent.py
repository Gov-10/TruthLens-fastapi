from strands import Agent, tool
from strands.models.gemini import GeminiModel
import requests, os
from dotenv import load_dotenv
from datetime import datetime
from requests.auth import HTTPBasicAuth
import urllib.parse
import logging
import asyncio
from realitydefender import RealityDefender
import aiohttp
import aiofiles
logging.basicConfig(level=logging.INFO)
load_dotenv()

model = GeminiModel(
    client_args={"api_key": os.getenv("GEMINI_API_KEY")},
    model_id="gemini-2.5-flash",
    params={"temperature": 0.4, "max_output_tokens": 2048, "top_p": 0.9, "top_k": 40}
)

@tool
def verify_text():
    """Return the fetched data from /reddit_war_news endpoint
    """
    data = requests.post("localhost:8080/reddit_war_news")
    if data.status_code == 200:
        return {"data" : data.json(), "code" : data.status_code}
    return {"code" : data.status_code}

verification_agent= Agent(model=model, tools=[verify_text])



    

