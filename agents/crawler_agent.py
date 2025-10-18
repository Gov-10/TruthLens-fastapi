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

from strands import Agent, tool
from strands.models.gemini import GeminiModel
from requests.auth import HTTPBasicAuth
import requests, os, urllib.parse
from dotenv import load_dotenv
from datetime import datetime
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)

@tool
def fetch_data(topic: str):
    """
    Fetch top 5 Reddit posts for any topic using official Reddit OAuth2 API.
    Auto-refreshes token if expired and filters for quality results.
    """
    topic = topic.strip() or "world news"
    query = urllib.parse.quote_plus(topic)

    # Step 1: Get access token
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
        logging.info("Reddit OAuth2 authentication successful.")
    except Exception as e:
        logging.error(f"OAuth2 failed: {e}")
        return {"error": f"OAuth2 failed: {e}"}

    # Step 2: Fetch data
    headers = {
        "Authorization": f"bearer {access_token}",
        "User-Agent": os.getenv("REDDIT_USER_AGENT"),
    }

    url = f"https://oauth.reddit.com/search?q={query}&limit=5&sort=top&type=link&restrict_sr=false"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 429:
            logging.warning("Rate limit hit — please wait before retrying.")
            return {"error": "429: Reddit API rate limit hit. Try again later."}
        res.raise_for_status()
        posts = res.json().get("data", {}).get("children", [])
    except Exception as e:
        logging.error(f"Reddit data fetch failed: {e}")
        return {"error": f"Reddit data fetch failed: {e}"}

    if not posts:
        return {"error": f"No Reddit posts found for topic: {topic}"}

    # Step 3: Parse results
    articles = []
    for p in posts:
        post_data = p.get("data", {})
        if not post_data.get("title"):  # skip incomplete posts
            continue
        articles.append({
            "headline": post_data.get("title"),
            "summary": (post_data.get("selftext") or "")[:400],
            "source": f"r/{post_data.get('subreddit', 'unknown')}",
            "url": "https://reddit.com" + post_data.get("permalink", ""),
            "timestamp": datetime.utcfromtimestamp(
                post_data.get("created_utc", 0)
            ).isoformat(timespec="seconds") + "Z",
            "upvotes": post_data.get("score", 0),
            "comments": post_data.get("num_comments", 0),
        })

    # Step 4: Return
    logging.info(f"Fetched {len(articles)} Reddit posts for '{topic}'.")
    return {"topic": topic, "articles": articles}

crawler_agent = Agent(model=model, tools=[fetch_data])
