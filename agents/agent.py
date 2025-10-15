from strands import Agent,tool
from strands.models.gemini import GeminiModel
import requests
import os
import environ
from dotenv import load_dotenv
load_dotenv()
env = environ.Env()
environ.Env.read_env()
model= GeminiModel(
    client_args= {
        "api_key": os.getenv("GEMINI_API_KEY")
    }, 
    model_id= "gemini-2.5-flash", 
    params= {
        "temperature" : 0.4, 
        "max_output_tokens": 2048, 
        "top_p" : 0.9, 
        "top_k" : 40
    }
)
@tool
def get_weather(city: str):
    """Fetch current weather of any city, and give a detailed analysis of weather conditions"""
    url = f"https://wttr.in/{city}?format=j1"
    data = requests.get(url, timeout=10).json()
    return data["current_condition"][0]

agent = Agent(model=model, tools=[get_weather])

