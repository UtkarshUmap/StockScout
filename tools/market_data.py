"""Tool 1: Market Data Fetcher — pulls price, fundamentals, and news from yfinance."""
import yfinance as yf
import pandas as pd
from typing import Optional


def fetch_price_history(ticker: str, period: str = "1y") -> Optional[pd.DataFrame]:
    """Fetch OHLCV price history.

    Args:
        ticker: e.g. 'RELIANCE.NS' or 'AAPL'
        period: '1mo', '3mo', '6mo', '1y', '2y', '5y'
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        return df if not df.empty else None
    except Exception as e:
        print(f"  [market_data] Error fetching {ticker}: {e}")
        return None


def fetch_fundamentals(ticker: str) -> dict:
    """Fetch fundamental metrics."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "ticker": ticker,
            "name": info.get("longName", ticker),
            "sector": info.get("sector", "Unknown"),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "pb_ratio": info.get("priceToBook"),
            "roe": info.get("returnOnEquity"),
            "debt_to_equity": info.get("debtToEquity"),
            "market_cap": info.get("marketCap"),
            "dividend_yield": info.get("dividendYield"),
        }
    except Exception as e:
        print(f"  [market_data] Error fetching fundamentals for {ticker}: {e}")
        return {"ticker": ticker, "name": ticker, "sector": "Unknown"}


def fetch_news(ticker: str, limit: int = 5) -> list:
    """Fetch recent news headlines."""
    try:
        stock = yf.Ticker(ticker)
        raw_news = stock.news[:limit] if stock.news else []
        results = []
        for item in raw_news:
            # yfinance has changed its news format; handle both old & new schemas
            content = item.get("content", item)
            title = content.get("title", "") if isinstance(content, dict) else ""
            provider = ""
            prov = content.get("provider") if isinstance(content, dict) else None
            if isinstance(prov, dict):
                provider = prov.get("displayName", "")
            elif isinstance(item.get("publisher"), str):
                provider = item["publisher"]
            summary = content.get("summary", "") if isinstance(content, dict) else ""
            if title:
                results.append({"title": title, "publisher": provider, "summary": summary})
        return results
    except Exception as e:
        print(f"  [market_data] Error fetching news for {ticker}: {e}")
        return []
