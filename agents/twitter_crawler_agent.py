import logging
logging.basicConfig(level=logging.INFO)
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
def fetch_tweets(topic: str):
    topic = topic.strip() or "world news"
    url = "https://api.twitter.com/2/tweets/search/recent"
    headers = {"Authorization": f"Bearer {os.getenv('TWITTER_BEARER_TOKEN')}"}
    params = {
        "query": topic,
        "max_results": 5,
        "tweet.fields": "created_at,public_metrics,lang,source,author_id",
        "expansions": "author_id"
    }

    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        logging.info(f"Twitter status: {res.status_code}")
        if res.status_code == 403:
            logging.error("403: Access tier does not include tweet search (upgrade required).")
            return {"error": "403: Your access tier does not include tweet search (upgrade required)."}
        if res.status_code == 401:
            logging.error("401: Unauthorized — invalid or expired bearer token.")
            return {"error": "401: Unauthorized — invalid bearer token."}
        if res.status_code == 429:
            logging.warning("429: Too many requests — rate limit hit.")
            return {"error": "429: Too many requests — rate limit reached."}
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        logging.exception("Twitter API request failed")
        return {"error": f"Twitter API request failed: {e}"}

    tweets = []
    for t in data.get("data", []):
        metrics = t.get("public_metrics", {})
        tweets.append({
            "headline": t["text"][:120],
            "summary": t["text"],
            "source": "Twitter (Official API)",
            "author": t.get("author_id", "unknown"),
            "url": f"https://twitter.com/i/web/status/{t['id']}",
            "timestamp": t["created_at"],
            "likes": metrics.get("like_count", 0),
            "retweets": metrics.get("retweet_count", 0)
        })

    if not tweets:
        logging.warning(f"No tweets found for topic: {topic}")
        return {"error": f"No tweets found for topic: {topic}"}

    return {"topic": topic, "tweets": tweets}

twitter_crawler_agent = Agent(model=model, tools=[fetch_tweets])
