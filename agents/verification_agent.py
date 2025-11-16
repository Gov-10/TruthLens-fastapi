from strands import Agent, tool
from strands.models.gemini import GeminiModel
import requests, os, logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

model = GeminiModel(
    client_args={"api_key": os.getenv("GEMINI_API_KEY")},
    model_id="gemini-2.5-flash",
    params={"temperature": 0.4, "max_output_tokens": 2048, "top_p": 0.9, "top_k": 40}
)

GNEWS_API = os.getenv("GNEWS_API_KEY")

@tool
def verify_text():
    """
    Fetch data from multiple Twitter and Reddit endpoints,
    aggregate them, and perform fact verification using GNews + Gemini.
    """
    endpoints = {
        "twitter_war_news": "http://localhost:8080/twitter_war_news",
        "twitter_politics_news": "http://localhost:8080/twitter_politics_news",
        "twitter_custom_news": "http://localhost:8080/twitter_custom_news",
        "twitter_natural_disaster_news": "http://localhost:8080/twitter_natural_disaster_news",
        "reddit_war_news": "http://localhost:8080/reddit_war_news",
        "reddit_politics_news" : "http://localhost:8080/reddit_politics_news",
        "reddit_natural_disaster_news": "http://localhost:8080/reddit_natural_disaster_news", 
        "reddit_custom_news" : "http://localhost:8080/reddit_custom_news"
    }

    all_articles = []
    for name, url in endpoints.items():
        try:
            res = requests.post(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                articles = data.get("articles", [])
                for a in articles:
                    a["source_type"] = name
                all_articles.extend(articles)
                logging.info(f"Fetched {len(articles)} posts from {name}")
            else:
                logging.warning(f"{name} returned {res.status_code}")
        except Exception as e:
            logging.error(f"Failed to fetch from {name}: {e}")

    if not all_articles:
        return {"error": "No data fetched from any endpoint"}

    verified_results = []
    for article in all_articles[:10]:
        claim = article.get("headline") or article.get("text") or ""
        if not claim.strip():
            continue

        try:
            gnews_url = f"https://gnews.io/api/v4/search?q={claim}&lang=en&token={GNEWS_API}"
            res = requests.get(gnews_url, timeout=10)
            res.raise_for_status()
            gnews_articles = res.json().get("articles", [])

            if not gnews_articles:
                verified_results.append({
                    "claim": claim,
                    "verdict": "Unverified",
                    "confidence": 0.0,
                    "explanation": "No related news found on GNews.",
                    "source_type": article.get("source_type"),
                })
                continue

            evidence = "\n".join(
                [f"- {a['title']}: {a.get('description', '')}" for a in gnews_articles[:3]]
            )
            prompt = f"""
You are a fact-checking agent. Given the following claim and evidence, decide if it's true, false, or unverified.

Claim:
"{claim}"

Evidence:
{evidence}

Respond strictly in JSON:
{{"verdict": "True/False/Unverified", "confidence": float (0-1), "explanation": "2-sentence reasoning"}}
"""
            verdict = model.prompt(prompt)
            verified_results.append({
                "claim": claim,
                "result": verdict,
                "source_type": article.get("source_type"),
            })

            logging.info(f"Verified claim from {article.get('source_type')}")
        except Exception as e:
            logging.error(f"Verification failed for '{claim[:40]}': {e}")

    return {"verified": verified_results, "total_checked": len(verified_results)}

verification_agent = Agent(model=model, tools=[verify_text])
