"""Tool 2: Signal Calculator — computes technical indicators and a rule-based score fallback."""
import pandas as pd
import numpy as np
from typing import Optional


# ---------- Technical indicators (pure pandas — no TA-Lib needed) ----------

def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index."""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """MACD line, signal line, and histogram."""
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


# ---------- Signal extraction ----------

def calculate_signals(price_df: pd.DataFrame, fundamentals: dict) -> Optional[dict]:
    """Compute all signals from price data + fundamentals."""
    if price_df is None or price_df.empty or len(price_df) < 50:
        return None

    close = price_df["Close"]
    volume = price_df["Volume"]
    current_price = float(close.iloc[-1])

    # RSI
    rsi_series = calculate_rsi(close)
    rsi = float(rsi_series.iloc[-1]) if not pd.isna(rsi_series.iloc[-1]) else 50.0

    # MACD
    _, _, hist = calculate_macd(close)
    macd_hist = float(hist.iloc[-1])
    macd_bullish = bool(hist.iloc[-1] > 0 and hist.iloc[-1] > hist.iloc[-2])

    # Moving averages
    sma_20 = float(close.rolling(20).mean().iloc[-1])
    sma_50 = float(close.rolling(50).mean().iloc[-1])
    sma_200 = float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else None

    above_sma_20 = current_price > sma_20
    above_sma_50 = current_price > sma_50
    above_sma_200 = (current_price > sma_200) if sma_200 else None
    golden_cross = (sma_50 > sma_200) if sma_200 else False

    # Momentum
    def pct_return(periods):
        if len(close) > periods:
            return ((close.iloc[-1] / close.iloc[-periods - 1]) - 1) * 100
        return 0.0

    return_1w = pct_return(5)
    return_1m = pct_return(21)
    return_3m = pct_return(63)

    # Volatility (annualized %)
    volatility = float(close.pct_change().std() * np.sqrt(252) * 100)

    # Volume spike
    avg_volume_20 = volume.rolling(20).mean().iloc[-1]
    volume_spike = ((volume.iloc[-1] / avg_volume_20) - 1) * 100 if avg_volume_20 > 0 else 0

    # 52-week range
    window = min(252, len(close))
    high_52w = close.rolling(window).max().iloc[-1]
    low_52w = close.rolling(window).min().iloc[-1]
    pct_from_high = ((current_price - high_52w) / high_52w) * 100
    pct_from_low = ((current_price - low_52w) / low_52w) * 100

    return {
        "current_price": round(current_price, 2),
        "rsi": round(rsi, 2),
        "macd_bullish": macd_bullish,
        "macd_histogram": round(macd_hist, 4),
        "above_sma_20": above_sma_20,
        "above_sma_50": above_sma_50,
        "above_sma_200": above_sma_200,
        "golden_cross": golden_cross,
        "return_1w": round(float(return_1w), 2),
        "return_1m": round(float(return_1m), 2),
        "return_3m": round(float(return_3m), 2),
        "volatility": round(volatility, 2),
        "volume_spike_pct": round(float(volume_spike), 2),
        "pct_from_52w_high": round(float(pct_from_high), 2),
        "pct_from_52w_low": round(float(pct_from_low), 2),
        "pe_ratio": fundamentals.get("pe_ratio"),
        "pb_ratio": fundamentals.get("pb_ratio"),
        "roe": fundamentals.get("roe"),
        "debt_to_equity": fundamentals.get("debt_to_equity"),
        "sector": fundamentals.get("sector"),
        "name": fundamentals.get("name"),
    }


# ---------- Rule-based scoring (fallback when no LLM) ----------

def rule_based_score(signals: dict) -> dict:
    """Compute scores using transparent rules — no LLM required."""
    if signals is None:
        return None

    technical = 50.0
    momentum = 50.0
    fundamental = 50.0

    # Technical (RSI, MACD, MAs)
    rsi = signals["rsi"]
    if rsi < 30:
        technical += 20  # oversold → bullish
    elif rsi > 70:
        technical -= 20  # overbought
    elif 40 <= rsi <= 60:
        technical += 5

    if signals["macd_bullish"]:
        technical += 10
    else:
        technical -= 5

    if signals["above_sma_20"]:
        technical += 5
    if signals["above_sma_50"]:
        technical += 10
    if signals["above_sma_200"]:
        technical += 10
    if signals["golden_cross"]:
        technical += 5

    # Momentum
    momentum += min(max(signals["return_1m"], -25), 25)
    momentum += min(max(signals["return_3m"] / 2, -25), 25)

    # Fundamental
    pe = signals.get("pe_ratio")
    if pe is not None and pe > 0:
        if pe < 15:
            fundamental += 15
        elif pe < 25:
            fundamental += 5
        elif pe > 40:
            fundamental -= 10

    roe = signals.get("roe")
    if roe is not None:
        if roe > 0.20:
            fundamental += 15
        elif roe > 0.10:
            fundamental += 5
        elif roe < 0:
            fundamental -= 15

    # Clamp 0-100
    technical = max(0, min(100, technical))
    momentum = max(0, min(100, momentum))
    fundamental = max(0, min(100, fundamental))

    # Build reasoning string
    reasons = []
    if rsi < 30:
        reasons.append(f"RSI {rsi:.1f} = oversold (bullish setup)")
    elif rsi > 70:
        reasons.append(f"RSI {rsi:.1f} = overbought (caution)")
    if signals["macd_bullish"]:
        reasons.append("MACD bullish crossover")
    if signals["golden_cross"]:
        reasons.append("Golden cross (50DMA > 200DMA)")
    if signals["return_1m"] > 5:
        reasons.append(f"Strong 1M return ({signals['return_1m']:.1f}%)")
    elif signals["return_1m"] < -5:
        reasons.append(f"Weak 1M return ({signals['return_1m']:.1f}%)")
    if pe and 0 < pe < 15:
        reasons.append(f"Attractive P/E ({pe:.1f})")
    if roe and roe > 0.20:
        reasons.append(f"High ROE ({roe*100:.1f}%)")

    return {
        "technical_score": round(technical, 1),
        "momentum_score": round(momentum, 1),
        "fundamental_score": round(fundamental, 1),
        "reasoning": "; ".join(reasons) if reasons else "Mixed signals across indicators",
    }
