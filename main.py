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
    return {"city": payload.city, "result": result}
