"""Configuration for StockScout."""

# Nifty 50 stocks (NSE India) — use .NS suffix for yfinance
NIFTY_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "BAJFINANCE.NS", "ASIANPAINT.NS", "MARUTI.NS",
    "HCLTECH.NS", "SUNPHARMA.NS", "TITAN.NS", "WIPRO.NS", "ULTRACEMCO.NS",
]

# US large-caps
US_STOCKS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
    "META", "TSLA", "JPM", "V", "WMT",
]

# Pick which universe to score — change this to switch markets
UNIVERSE = NIFTY_STOCKS

# Composite score weights (must sum to 1.0)
WEIGHTS = {
    "technical": 0.35,
    "momentum": 0.25,
    "fundamental": 0.20,
    "sentiment": 0.20,
}

# Recommendation thresholds (composite score)
THRESHOLDS = {
    "STRONG BUY": 75,
    "BUY": 60,
    "HOLD": 45,
    "SELL": 30,
    # below 30 = STRONG SELL
}
