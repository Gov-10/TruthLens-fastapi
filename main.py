from fastapi import FastAPI
from pydantic import BaseModel
from agents.agent import agent
app = FastAPI()

class CityInput(BaseModel):
    city: str

@app.post("/fetch")
async def fetch_weather(payload: CityInput):
    query = f"Give me the current weather and clothing recommendations for {payload.city}."
    result = agent(query)
    print("Type of result:", type(result))
    print("Keys:", getattr(result, "__dict__", result if isinstance(result, dict) else None))
    return {"city": payload.city, "result": result.message["content"][0]["text"]}
