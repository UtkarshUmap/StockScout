"""Scoring Agent — orchestrates the 3 tools and produces a final score per stock."""
import os
import json
from typing import Optional

from tools.market_data import fetch_price_history, fetch_fundamentals, fetch_news
from tools.signal_calculator import calculate_signals, rule_based_score
from tools.news_sentiment import analyze_sentiment
from agent.prompts import SCORING_PROMPT
from config import WEIGHTS, THRESHOLDS


def get_llm_provider() -> str:
    return os.getenv("LLM_PROVIDER", "mock").lower()


def _recommendation_from_score(score: float) -> str:
    if score >= THRESHOLDS["STRONG BUY"]:
        return "STRONG BUY"
    if score >= THRESHOLDS["BUY"]:
        return "BUY"
    if score >= THRESHOLDS["HOLD"]:
        return "HOLD"
    if score >= THRESHOLDS["SELL"]:
        return "SELL"
    return "STRONG SELL"


def _extract_json(text: str) -> dict:
    text = text.strip()
    if "```" in text:
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def _llm_score(signals: dict, sentiment: dict, ticker: str) -> Optional[dict]:
    """Ask the LLM to produce a structured score with reasoning."""
    provider = get_llm_provider()
    if provider == "mock":
        return None

    rsi = signals["rsi"]
    rsi_interp = "OVERSOLD" if rsi < 30 else "OVERBOUGHT" if rsi > 70 else "NEUTRAL"
    macd_status = "BULLISH" if signals["macd_bullish"] else "BEARISH"

    prompt = SCORING_PROMPT.format(
        ticker=ticker,
        name=signals.get("name", ticker),
        sector=signals.get("sector", "Unknown"),
        current_price=signals["current_price"],
        rsi=signals["rsi"],
        rsi_interp=rsi_interp,
        macd_histogram=signals["macd_histogram"],
        macd_status=macd_status,
        above_sma_20=signals["above_sma_20"],
        above_sma_50=signals["above_sma_50"],
        above_sma_200=signals["above_sma_200"],
        golden_cross=signals["golden_cross"],
        return_1w=signals["return_1w"],
        return_1m=signals["return_1m"],
        return_3m=signals["return_3m"],
        volatility=signals["volatility"],
        pct_from_52w_high=signals["pct_from_52w_high"],
        pct_from_52w_low=signals["pct_from_52w_low"],
        pe_ratio=signals.get("pe_ratio") or "N/A",
        pb_ratio=signals.get("pb_ratio") or "N/A",
        roe=signals.get("roe") or "N/A",
        debt_to_equity=signals.get("debt_to_equity") or "N/A",
        sentiment_score=sentiment["sentiment_score"],
        sentiment_label=sentiment["sentiment_label"],
        sentiment_summary=sentiment["summary"],
    )

    try:
        if provider == "groq":
            from groq import Groq
            client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=600,
            )
            return _extract_json(response.choices[0].message.content)

        if provider == "anthropic":
            from anthropic import Anthropic
            client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}],
            )
            return _extract_json(response.content[0].text)
    except Exception as e:
        print(f"  [agent] LLM error for {ticker}: {e}")
        return None

    return None


def score_stock(ticker: str) -> Optional[dict]:
    """Full pipeline for one stock: fetch → signals → sentiment → score."""
    print(f"  Processing {ticker}...")

    # 1. Market data
    price_df = fetch_price_history(ticker, period="1y")
    if price_df is None or price_df.empty:
        print(f"    ✗ No price data")
        return None
    fundamentals = fetch_fundamentals(ticker)

    # 2. Signals
    signals = calculate_signals(price_df, fundamentals)
    if signals is None:
        print(f"    ✗ Insufficient data")
        return None

    # 3. News + sentiment
    news = fetch_news(ticker, limit=5)
    sentiment = analyze_sentiment(news, ticker, get_llm_provider())

    # 4. Final scoring (LLM or rules)
    llm = _llm_score(signals, sentiment, ticker)

    if llm:
        result = {
            **signals,
            "ticker": ticker,
            "sentiment_score": sentiment["sentiment_score"],
            "sentiment_label": sentiment["sentiment_label"],
            **llm,
        }
    else:
        rb = rule_based_score(signals)
        composite = (
            WEIGHTS["technical"] * rb["technical_score"]
            + WEIGHTS["momentum"] * rb["momentum_score"]
            + WEIGHTS["fundamental"] * rb["fundamental_score"]
            + WEIGHTS["sentiment"] * sentiment["sentiment_score"]
        )
        result = {
            **signals,
            "ticker": ticker,
            "technical_score": rb["technical_score"],
            "momentum_score": rb["momentum_score"],
            "fundamental_score": rb["fundamental_score"],
            "sentiment_score": sentiment["sentiment_score"],
            "sentiment_label": sentiment["sentiment_label"],
            "composite_score": round(composite, 1),
            "recommendation": _recommendation_from_score(composite),
            "reasoning": rb["reasoning"],
            "entry_signal": "Wait for confirmation" if composite < 60 else "Setup looks favorable",
            "key_risks": "Market volatility and sector-specific risks apply",
        }

    print(f"    ✓ Score: {result['composite_score']:.1f}  [{result['recommendation']}]")
    return result


def score_universe(tickers: list) -> list:
    """Score a list of stocks and return them sorted (highest score first)."""
    results = []
    for ticker in tickers:
        try:
            r = score_stock(ticker)
            if r:
                results.append(r)
        except Exception as e:
            print(f"  ✗ {ticker} failed: {e}")
    results.sort(key=lambda x: x["composite_score"], reverse=True)
    return results
