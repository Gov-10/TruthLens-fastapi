from fastapi import FastAPI
from pydantic import BaseModel
from agents.agent import agent
from agents.crawler_agent import crawler_agent
from typing import Dict
app = FastAPI()

class CityInput(BaseModel):
    city: str

@app.post("/fetch")
async def fetch_weather(payload: CityInput):
    query = f"Give me the current weather and clothing recommendations for {payload.city}."
    result = agent(query)
    print("Type of result:", type(result))
    print("Keys:", getattr(result, "__dict__", result if isinstance(result, dict) else None))
    return {"city": payload.city, "result": result.message["content"][0]["text"] }

@app.post("/fetch_data", response_model=Dict[str, str])
async def fetch_data()-> Dict[str, str]:
    query = "Fetch top 5 trending news around the world"
    result=crawler_agent(query)
    print("type of result:", type(result))
    print("keys:", getattr(result, "__dict__", result if isinstance(result, dict) else None))
    return {"result": result.message["content"][0]["text"]}


