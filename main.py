from fastapi import FastAPI
from pydantic import BaseModel
from agents.agent import agent
from agents.crawler_agent import crawler_agent
from typing import Dict
from agents.twitter_crawler_agent import twitter_crawler_agent
from agents.fake_detector_agent import fake_detector_agent
app = FastAPI()

class CityInput(BaseModel):
    city: str

class TopicInput(BaseModel):
    topic : str

@app.post("/fetch")
async def fetch_weather(payload: CityInput):
    query = f"Give me the current weather and clothing recommendations for {payload.city}."
    result = agent(query)
    print("Type of result:", type(result))
    print("Keys:", getattr(result, "__dict__", result if isinstance(result, dict) else None))
    return {"city": payload.city, "result": result.message["content"][0]["text"] }

#REDDIT DATA FETCHING
@app.post("/reddit_war_news", response_model=Dict[str, str])
async def fetch_data()-> Dict[str, str]:
    query = "Fetch top 5 trending war news from Reddit"
    result=crawler_agent(query)
    print("type of result:", type(result))
    print("keys:", getattr(result, "__dict__", result if isinstance(result, dict) else None))
    return {"result": result.message["content"][0]["text"]}

@app.post("/reddit_politics_news", response_model=Dict[str, str])
async def fetch_data()-> Dict[str, str]:
    query = "Fetch top 5 trending politics news from Reddit"
    result=crawler_agent(query)
    print("type of result:", type(result))
    print("keys:", getattr(result, "__dict__", result if isinstance(result, dict) else None))
    return {"result": result.message["content"][0]["text"]}

@app.post("/reddit_natural_disaster_news", response_model=Dict[str, str])
async def fetch_data()-> Dict[str, str]:
    query = "Fetch top 5 trending natural disaster news from Reddit"
    result=crawler_agent(query)
    print("type of result:", type(result))
    print("keys:", getattr(result, "__dict__", result if isinstance(result, dict) else None))
    return {"result": result.message["content"][0]["text"]}

@app.post("/reddit_custom", response_model=Dict[str, str])
async def fetch_data(payload: TopicInput)-> Dict[str, str]:
    query = f"Fetch top 5 trending news headlines for {payload.topic} from Reddit"
    result= crawler_agent(query)
    print("type of result:", type(result))
    print("keys:", getattr(result, "__dict__", result if isinstance(result, dict) else None))
    return {"result": result.message["content"][0]["text"]}


#TWITTER DATA FETCHING
@app.post("/twitter_war_news", response_model=Dict[str, str])
async def fetch_data()-> Dict[str, str]:
    query = "war"
    result=twitter_crawler_agent(query)
    print("type of result:", type(result))
    print("keys:", getattr(result, "__dict__", result if isinstance(result, dict) else None))
    return {"result": result.message["content"][0]["text"]}

@app.post("/twitter_politics_news", response_model=Dict[str, str])
async def fetch_data()-> Dict[str, str]:
    query = "politics"
    result=twitter_crawler_agent(query)
    print("type of result:", type(result))
    print("keys:", getattr(result, "__dict__", result if isinstance(result, dict) else None))
    return {"result": result.message["content"][0]["text"]}

@app.post("/twitter_natural_disaster_news", response_model=Dict[str, str])
async def fetch_data()-> Dict[str, str]:
    query = "natural disaster"
    result=twitter_crawler_agent(query)
    print("type of result:", type(result))
    print("keys:", getattr(result, "__dict__", result if isinstance(result, dict) else None))
    return {"result": result.message["content"][0]["text"]}

@app.post("/twitter_custom", response_model=Dict[str, str])
async def fetch_data(payload: TopicInput)-> Dict[str, str]:
    query = f"Fetch top 5 trending news headlines for {payload.topic} from Twitter"
    result= twitter_crawler_agent(query)
    print("type of result:", type(result))
    print("keys:", getattr(result, "__dict__", result if isinstance(result, dict) else None))
    return {"result": result.message["content"][0]["text"]}

#FAKE DETECTOR AGENT
class UrlInput(BaseModel):
    url_input : str
@app.post("/detector", response_model=Dict[str, str])
async def detect_fake(payload: UrlInput)-> Dict[str, str]:
    query =f"check whether the following content is AI-generated and fake or real {payload.url_input}"
    result = fake_detector_agent(query)
    print("type of result:", type(result))
    print("keys:", getattr(result, "__dict__", result if isinstance(result, dict) else None))
    return {"result": result.message["content"][0]["text"]}

