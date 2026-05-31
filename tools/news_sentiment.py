"""Tool 3: News Sentiment Analyzer — uses LLM or keyword fallback."""
import os
import json
from typing import List


def analyze_sentiment(news_items: List[dict], ticker: str, llm_provider: str = "mock") -> dict:
    """Analyze sentiment from a list of news headlines.

    Returns a dict with: sentiment_score (0-100), sentiment_label, summary
    """
    if not news_items:
        return {
            "sentiment_score": 50,
            "sentiment_label": "NEUTRAL",
            "summary": "No recent news available",
        }

    headlines = "\n".join(f"- {item['title']}" for item in news_items if item.get("title"))
    if not headlines.strip():
        return {"sentiment_score": 50, "sentiment_label": "NEUTRAL", "summary": "No headlines"}

    if llm_provider == "groq":
        return _call_groq(headlines, ticker)
    if llm_provider == "anthropic":
        return _call_anthropic(headlines, ticker)
    return _keyword_sentiment(headlines)


# ---------- Mock / keyword sentiment ----------

POSITIVE_WORDS = [
    "surge", "soar", "rally", "gain", "rise", "beat", "growth", "profit", "upgrade",
    "strong", "record", "high", "outperform", "bullish", "boost", "expand", "wins",
    "approves", "launches", "innovative",
]
NEGATIVE_WORDS = [
    "fall", "drop", "plunge", "loss", "decline", "miss", "downgrade", "weak",
    "concern", "risk", "low", "cut", "bearish", "lawsuit", "investigation",
    "fraud", "scandal", "warns", "fires", "layoff",
]


def _keyword_sentiment(headlines: str) -> dict:
    text = headlines.lower()
    pos = sum(w in text for w in POSITIVE_WORDS)
    neg = sum(w in text for w in NEGATIVE_WORDS)

    if pos + neg == 0:
        return {"sentiment_score": 50, "sentiment_label": "NEUTRAL", "summary": "Neutral coverage"}

    score = 50 + (pos - neg) * 10
    score = max(0, min(100, score))
    label = "POSITIVE" if score >= 65 else "NEGATIVE" if score <= 35 else "NEUTRAL"
    return {
        "sentiment_score": score,
        "sentiment_label": label,
        "summary": f"Keyword analysis: {pos} positive vs {neg} negative signals",
    }


# ---------- LLM calls ----------

_PROMPT_TMPL = """Analyze the sentiment of these news headlines for stock {ticker}.

Headlines:
{headlines}

Respond with ONLY a JSON object (no markdown, no extra text):
{{"sentiment_score": <0-100 number>, "sentiment_label": "<POSITIVE|NEUTRAL|NEGATIVE>", "summary": "<one sentence>"}}"""


def _extract_json(text: str) -> dict:
    text = text.strip()
    if "```" in text:
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def _call_groq(headlines: str, ticker: str) -> dict:
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": _PROMPT_TMPL.format(ticker=ticker, headlines=headlines)}],
            temperature=0.1,
            max_tokens=200,
        )
        return _extract_json(response.choices[0].message.content)
    except Exception as e:
        print(f"  [sentiment] Groq error: {e} → falling back to keywords")
        return _keyword_sentiment(headlines)


def _call_anthropic(headlines: str, ticker: str) -> dict:
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[{"role": "user", "content": _PROMPT_TMPL.format(ticker=ticker, headlines=headlines)}],
        )
        return _extract_json(response.content[0].text)
    except Exception as e:
        print(f"  [sentiment] Anthropic error: {e} → falling back to keywords")
        return _keyword_sentiment(headlines)
