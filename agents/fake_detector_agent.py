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
   """
    Detect if a given text is AI-generated using ZeroGPT API.
    Returns probability and verdict (AI-generated or human-written).
    """
    url = "https://api.zerogpt.com/v1/detect/text"
    headers = {"Authorization": f"Bearer {os.getenv('ZEROGPT_API_KEY')}"}
    payload = {"text": text}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        result = data.get("data", {})
        return {
            "source": "ZeroGPT",
            "ai_probability": result.get("ai_probability"),
            "human_probability": result.get("human_probability"),
            "verdict": result.get("verdict", "Unknown"),
        }
    except Exception as e:
        logging.error(f"ZeroGPT API Error: {e}")
        return {"error": str(e), "verdict": "Unknown"}

@tool 
def detect_ai_image(image_url : str):
    """
    Detect if an image is AI-generated or manipulated using Reality Defender API.
    """
    url = "https://api.realitydefender.ai/v1/detect"
    headers = {
        "x-api-key": os.getenv("REALITY_DEFENDER_API_KEY"),
        "Content-Type": "application/json",
    }
    payload = {"url": image_url, "type": "image"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        analysis = result.get("result", {}).get("label", "Unknown")
        confidence = result.get("result", {}).get("confidence", "N/A")
        return {
            "source": "Reality Defender",
            "label": analysis,
            "confidence": confidence,
        }
    except Exception as e:
        logging.error(f"Reality Defender Image Error: {e}")
        return {"error": str(e), "label": "Unknown"}

@tool
def detect_ai_video(video_url : str):
    """
    Detect if a given video contains deepfake content using Reality Defender API.
    """
    url = "https://api.realitydefender.ai/v1/detect"
    headers = {
        "x-api-key": os.getenv("REALITY_DEFENDER_API_KEY"),
        "Content-Type": "application/json",
    }
    payload = {"url": video_url, "type": "video"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        result = response.json()
        analysis = result.get("result", {}).get("label", "Unknown")
        confidence = result.get("result", {}).get("confidence", "N/A")
        return {
            "source": "Reality Defender",
            "label": analysis,
            "confidence": confidence,
        }
    except Exception as e:
        logging.error(f"Reality Defender Video Error: {e}")
        return {"error": str(e), "label": "Unknown"}


fake_detector_agent = Agent(model=model, tools= [detect_ai_text, detect_ai_image, detect_ai_video])
