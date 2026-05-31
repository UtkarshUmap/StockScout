# 📊 StockScout — AI Stock Scoring Agent

An agentic AI project that scores stocks daily using **3 tools** (market data, technical signals, news sentiment) and produces a ranked dashboard with buy/sell recommendations and reasoning.

## What this project demonstrates

This is a course-grade agentic AI build that shows:

- **Multi-tool orchestration** — the agent calls 3 specialized tools in sequence
- **LLM reasoning** — the agent doesn't just compute numbers, it explains its score
- **Graceful fallback** — works even without an API key (rule-based mode)
- **End-to-end pipeline** — fetch → process → reason → rank → visualize
- **Real data** — uses live market data via yfinance (no paid APIs needed)

## Architecture

```
        ┌──────────────────────────────────────────┐
        │           Scoring Agent                  │
        │     (orchestrator + LLM reasoner)        │
        └──────────────────────────────────────────┘
              │             │             │
              ▼             ▼             ▼
        ┌─────────┐  ┌─────────────┐  ┌───────────┐
        │ Tool 1  │  │  Tool 2     │  │  Tool 3   │
        │ Market  │  │  Signal     │  │  News     │
        │ Data    │  │  Calculator │  │  Sentiment│
        │ yfinance│  │  (pandas)   │  │  (LLM)    │
        └─────────┘  └─────────────┘  └───────────┘
              │             │             │
              └─────────────┼─────────────┘
                            ▼
              ┌──────────────────────────┐
              │   Composite Score (0-100)│
              │   Recommendation         │
              │   Reasoning              │
              └──────────────────────────┘
                            │
                            ▼
                ┌──────────────────────┐
                │ Streamlit Dashboard  │
                │ (sorted, filterable) │
                └──────────────────────┘
```

## Scoring formula

```
composite_score = 0.35 × technical_score
                + 0.25 × momentum_score
                + 0.20 × fundamental_score
                + 0.20 × sentiment_score
```

Recommendation thresholds: **STRONG BUY** ≥75 · **BUY** ≥60 · **HOLD** 45–59 · **SELL** 30–44 · **STRONG SELL** <30

---

## 🚀 Setup (5 minutes)

### 1. Install Python 3.10+

Check with: `python --version`

### 2. Unzip and enter the project folder

```bash
cd stockscout
```

### 3. Create a virtual environment

```bash
# macOS / Linux
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Set up environment variables

```bash
cp .env.example .env
```

Open `.env` and choose one of three modes:

**Option A — Mock mode (no API key, works immediately)**
```
LLM_PROVIDER=mock
```
Uses rule-based scoring + keyword sentiment. Perfect for testing.

**Option B — Groq (FREE, recommended)**
1. Get a free key at https://console.groq.com/keys
2. Edit `.env`:
```
LLM_PROVIDER=groq
GROQ_API_KEY=your_key_here
```

**Option C — Anthropic Claude**
1. Get a key at https://console.anthropic.com
2. Edit `.env`:
```
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key_here
```

---

## ▶️ How to run

### Option 1: Run scoring from command line

```bash
python run_scoring.py
```

You'll see output like:
```
============================================================
  StockScout — Daily Scoring Run
  Date: 2026-05-31 10:00:00
  LLM Provider: groq
  Universe size: 20 stocks
============================================================

  Processing RELIANCE.NS...
    ✓ Score: 68.4  [BUY]
  Processing TCS.NS...
    ✓ Score: 72.1  [BUY]
  ...

TOP 5 BY SCORE:
  1. TCS.NS              72.1  [BUY]
  2. INFY.NS             71.2  [BUY]
  ...
```

Results are saved to `data/scores_latest.csv`.

### Option 2: Launch the dashboard

```bash
streamlit run app.py
```

Opens at **http://localhost:8501**. Click **"Run Daily Scoring"** in the sidebar to populate data.

The dashboard shows:
- 📈 Ranked table (color-coded by recommendation)
- 🔍 Click any stock for detailed view (candlestick chart, RSI, score breakdown, agent reasoning)
- Filter and sort by any score component

---

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Switch to US stocks
UNIVERSE = US_STOCKS

# Add your own
UNIVERSE = ["RELIANCE.NS", "AAPL", "TSLA"]

# Change scoring weights
WEIGHTS = {
    "technical": 0.40,
    "momentum": 0.30,
    "fundamental": 0.15,
    "sentiment": 0.15,
}
```

---

## 📁 Project structure

```
stockscout/
├── README.md
├── requirements.txt
├── .env.example
├── config.py                  # Universe + weights
├── run_scoring.py             # CLI entrypoint
├── app.py                     # Streamlit dashboard
├── tools/
│   ├── market_data.py         # Tool 1: yfinance wrapper
│   ├── signal_calculator.py   # Tool 2: technical indicators
│   └── news_sentiment.py      # Tool 3: news + LLM sentiment
├── agent/
│   ├── scoring_agent.py       # Orchestrator
│   └── prompts.py             # LLM prompt templates
└── data/
    └── scores_latest.csv      # Output (generated)
```

---

## 🎓 For your course report

Strong talking points to include:

1. **Agentic design** — the agent autonomously calls 3 tools per stock in sequence and synthesizes their outputs
2. **Tool abstraction** — each tool is independent and swappable (could replace yfinance with Alpha Vantage tomorrow)
3. **LLM-as-reasoner** — used not to fetch facts, but to weigh evidence and produce explanations
4. **Graceful degradation** — mock mode shows the system works even when the LLM is unavailable
5. **Real-world data** — handles missing data, API errors, and rate limits gracefully

### Possible extensions (for bonus marks)
- **Backtesting** — replay the scoring on past dates and measure prediction accuracy
- **Email/Telegram alerts** when a stock crosses into STRONG BUY
- **Portfolio mode** — score your existing holdings and suggest rebalances
- **Sector rotation** — aggregate scores by sector
- **Schedule it** — run daily via cron (`0 18 * * * cd /path/to/stockscout && python run_scoring.py`)

---

## ⚠️ Disclaimer

This is an educational project for an agentic AI course. **Not financial advice.** Stock prediction is fundamentally hard and no scoring system can reliably forecast markets. The "score" reflects favorable signal alignment — not guaranteed profit. Past performance does not guarantee future results.

---

## 🐛 Troubleshooting

**"No price data" for a ticker** — yfinance occasionally rate-limits or fails for certain tickers. Re-run, or remove that ticker.

**"Module not found"** — make sure your venv is activated and you ran `pip install -r requirements.txt`.

**Streamlit not opening** — try `streamlit run app.py --server.port 8502` if port 8501 is busy.

**LLM errors** — verify your API key in `.env` and that you have credits. The agent will fall back to rule-based scoring on LLM errors.
