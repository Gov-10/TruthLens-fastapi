from strands import Agent, tool
from strands.models.gemini import GeminiModel
import requests, os
from dotenv import load_dotenv
from datetime import datetime
from requests.auth import HTTPBasicAuth
import urlib.parse
import logging

logging.basicConfig(level=logging.INFO)
load_dotenv()

model = GeminiModel(
    client_args={"api_key": os.getenv("GEMINI_API_KEY")},
    model_id="gemini-2.5-flash",
    params={"temperature": 0.4, "max_output_tokens": 2048, "top_p": 0.9, "top_k": 40}
)

@tool
def verify_text(news: dict):
    """Verify input text's authenticity using google factcheck API and GNews API.
    Return verified summaries, credibility scores and factual verdicts.
    """
    

