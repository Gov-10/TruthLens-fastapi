from strands import Agent, tool
from strands.models.gemini import GeminiModel
import requests, os
from dotenv import load_dotenv
from datetime import datetime
from requests.auth import HTTPBasicAuth
import urllib.parse
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
    """Detect AI-generated text using ZeroGPT official API. Give a verdict, probability and explanation supporting your verdict"""
    import os, requests, json, logging
    url = "https://api.zerogpt.com/api/detect/detectText"
    api_key = os.getenv("ZEROGPT_API_KEY")
    if not api_key:
        return {"error": "Missing ZeroGPT API key in environment variables", "verdict": "Unknown"}
    headers = {
        "ApiKey": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = json.dumps({"input_text": text})
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        logging.info(f"ZeroGPT raw response: {data}")
        if not data.get("success", False):
            return {
                "error": str(data.get("message", "ZeroGPT internal error")),
                "code": int(data.get("code", 500)),
                "verdict": "Unknown"
            }
        result = data.get("data") or {}
        return {
            "source": "ZeroGPT",
            "ai_confidence": float(100 - result.get("isHuman", 0)),
            "human_confidence": float(result.get("isHuman", 0)),
            "feedback": str(result.get("feedback", "Unknown")),
            "fakePercentage": float(result.get("fakePercentage", 0.0)),
            "language": str(result.get("detected_language", "Unknown")),
            "verdict": "AI-generated" if result.get("isHuman", 0) < 50 else "Human-written"
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
