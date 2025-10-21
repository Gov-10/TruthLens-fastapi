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
def detect_ai_text(text: str):
    """Detect if a given text is AI-generated using Hive Hibernation API
     Also, give your verdict on its authenticity using any sources
     """
    url = "https://api.thehive.ai/api/v2/task/sync"
    hive_api_key = os.getenv("HIVE_API_KEY")
    headers = {
        "Authorization" : f"Token {hive_api_key}"
    }
    payload = {"models": ["ai-generated-text-detector"], "text": text}
    response = requests.post(url, json=payload, headers=headers, timeout=15)
    result = response.json()
    return result

@tool 
def detect_ai_image(image_url : str):
    """ Detect if a given image is AI-generated using Hive Hibernate API
    Also, give your verdict on its authenticity using any source you want
    """
    url = "https://api.thehive.ai/api/v2/task/sync"
    headers = {"Authorization": f"Token {os.getenv('HIVE_API_KEY')}"}
    payload = {
        "models": ["ai-generated-image-detector"],
        "url": image_url
    }
    response = requests.post(url, json=payload, headers=headers, timeout=15)
    return response.json()

@tool
def detect_ai_video(video_url : str):
    """ Detect if a given video is AI-generated and contains deepfake content
    Also, give your verdict on its authenticity using any source you want
    """
    url = "https://api.deepware.ai/api/v1/detect"
    headers = {"Authorization": f"Bearer {os.getenv('DEEPWARE_API_KEY')}"}
    payload = {"url": video_url}
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    return response.json()

fake_detector_agent = Agent(model=model, tools= [detect_ai_text, detect_ai_image, detect_ai_video])
