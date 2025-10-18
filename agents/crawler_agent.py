from strands import Agent, tool
from strands.models.gemini import GeminiModel
import requests, os
from dotenv import load_dotenv

load_dotenv()

model = GeminiModel(
    client_args={"api_key": os.getenv("GEMINI_API_KEY")},
    model_id="gemini-2.5-flash",
    params={"temperature": 0.4, "max_output_tokens": 2048, "top_p": 0.9, "top_k": 40}
)

@tool
def fetch_data(topic: str):
    """Fetch top 5 news headlines related to a specific topic."""
    key = os.getenv("GNEWS_API_KEY")
    url = f"https://gnews.io/api/v4/search?q={topic}%20misinformation&lang=en&max=5&token={key}"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        return {"error": str(e)}

    if not data.get("articles"):
        return {"error": "No articles found for this topic"}

    articles = [
        {
            "title": art.get("title"),
            "description": art.get("description"),
            "source": art.get("source", {}).get("name"),
            "url": art.get("url"),
            "publishedAt": art.get("publishedAt")
        }
        for art in data["articles"]
    ]
    return {"topic": topic, "articles": articles}

crawler_agent = Agent(model=model, tools=[fetch_data])