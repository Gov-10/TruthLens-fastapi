from strands import Agent, tool
from strands.models.gemini import GeminiModel
import requests, os
from dotenv import load_dotenv
from datetime import datetime
from requests.auth import HTTPBasicAuth

load_dotenv()

model = GeminiModel(
    client_args={"api_key": os.getenv("GEMINI_API_KEY")},
    model_id="gemini-2.5-flash",
    params={"temperature": 0.4, "max_output_tokens": 2048, "top_p": 0.9, "top_k": 40}
)

@tool
def fetch_data(topic: str):
    """
    Fetch top 5 Reddit posts for any topic using official Reddit OAuth2 API.
    Falls back to 'world news' if topic is empty.
    """
    topic = topic.strip() or "world news"
    auth = HTTPBasicAuth(os.getenv("REDDIT_CLIENT_ID"), os.getenv("REDDIT_CLIENT_SECRET"))
    data = {"grant_type": "client_credentials"}
    headers = {"User-Agent": os.getenv("REDDIT_USER_AGENT")}
    try:
        token_res = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=auth,
            data=data,
            headers=headers,
            timeout=10
        )
        token_res.raise_for_status()
        access_token = token_res.json()["access_token"]
    except Exception as e:
        return {"error": f"OAuth2 failed: {e}"}
    headers = {
        "Authorization": f"bearer {access_token}",
        "User-Agent": os.getenv("REDDIT_USER_AGENT"),
    }
    url = f"https://oauth.reddit.com/search?q={topic}&limit=5&sort=hot&type=link"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        posts = res.json().get("data", {}).get("children", [])
    except Exception as e:
        return {"error": f"Reddit data fetch failed: {e}"}
    if not posts:
        return {"error": f"No Reddit posts found for topic: {topic}"}
    articles = [
        {
            "headline": p["data"].get("title"),
            "summary": (p["data"].get("selftext") or "")[:400],
            "source": f"r/{p['data'].get('subreddit', 'unknown')}",
            "url": "https://reddit.com" + p["data"].get("permalink", ""),
            "timestamp": datetime.utcfromtimestamp(
                p["data"].get("created_utc", 0)
            ).isoformat() + "Z",
        }
        for p in posts if p.get("data")
    ]
    return {"topic": topic, "articles": articles}


crawler_agent = Agent(model=model, tools=[fetch_data])
