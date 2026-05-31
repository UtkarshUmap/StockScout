"""Prompt templates for the scoring agent."""

SCORING_PROMPT = """You are a quantitative stock analyst. Score the following stock based on the signals provided.

STOCK: {ticker} ({name})
Sector: {sector}
Current Price: {current_price}

TECHNICAL:
- RSI(14): {rsi} ({rsi_interp})
- MACD Histogram: {macd_histogram} ({macd_status})
- Price > 20-day MA: {above_sma_20}
- Price > 50-day MA: {above_sma_50}
- Price > 200-day MA: {above_sma_200}
- Golden Cross (50DMA > 200DMA): {golden_cross}

MOMENTUM:
- 1-Week return: {return_1w}%
- 1-Month return: {return_1m}%
- 3-Month return: {return_3m}%
- Annualized volatility: {volatility}%
- Distance from 52w high: {pct_from_52w_high}%
- Distance from 52w low: {pct_from_52w_low}%

FUNDAMENTAL:
- P/E: {pe_ratio}
- P/B: {pb_ratio}
- ROE: {roe}
- Debt/Equity: {debt_to_equity}

NEWS SENTIMENT:
- Score: {sentiment_score}/100 ({sentiment_label})
- Summary: {sentiment_summary}

Return ONLY a JSON object with these exact fields (no markdown, no extra text):
{{
  "technical_score": <0-100>,
  "momentum_score": <0-100>,
  "fundamental_score": <0-100>,
  "composite_score": <0.35*tech + 0.25*momentum + 0.20*fundamental + 0.20*sentiment>,
  "recommendation": "<STRONG BUY|BUY|HOLD|SELL|STRONG SELL>",
  "reasoning": "<2-3 sentences explaining the score>",
  "entry_signal": "<concrete buy condition or 'avoid'>",
  "key_risks": "<one sentence on main risks>"
}}

Thresholds: STRONG BUY ≥75, BUY ≥60, HOLD 45-59, SELL 30-44, STRONG SELL <30.
"""
