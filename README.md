# 📊 StockScout

StockScout is a stock analysis dashboard that combines technical indicators, momentum metrics, fundamental data, and news sentiment into a single composite score.

The project fetches market data, evaluates multiple signals, ranks stocks, and presents the results through an interactive Streamlit dashboard.

## Features

* Technical analysis using RSI and moving averages
* Momentum scoring based on historical returns
* Fundamental scoring from company metrics
* News sentiment analysis
* Composite scoring system
* Buy / Hold / Sell recommendations
* Interactive Streamlit dashboard
* Candlestick charts with RSI visualization
* Filterable and sortable stock rankings

## Tech Stack

* Python
* Streamlit
* Pandas
* Plotly
* yfinance
* Python-dotenv

## Project Structure

```text
stockscout/
├── app.py
├── run_scoring.py
├── config.py
├── requirements.txt
├── agent/
│   ├── scoring_agent.py
│   └── prompts.py
├── tools/
│   ├── market_data.py
│   ├── signal_calculator.py
│   └── news_sentiment.py
└── data/
```

## Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/stockscout.git
cd stockscout
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create an environment file:

```bash
cp .env.example .env
```

Configure the required API keys if needed.

## Running the Scoring Pipeline

```bash
python run_scoring.py
```

The generated scores are stored in the `data/` directory.

## Running the Dashboard

```bash
streamlit run app.py
```

The application will be available at:

```text
http://localhost:8501
```

## Scoring Methodology

The final score is calculated using weighted components:

| Component   | Weight |
| ----------- | ------ |
| Technical   | 35%    |
| Momentum    | 25%    |
| Fundamental | 20%    |
| Sentiment   | 20%    |

The resulting score is converted into a recommendation category:

* STRONG BUY
* BUY
* HOLD
* SELL
* STRONG SELL

## Future Improvements

* Portfolio tracking
* Historical backtesting
* Alert notifications
* Additional technical indicators
* Sector-level analysis
* Automated scheduled runs

## Disclaimer

This project is intended for educational and research purposes only and should not be considered financial advice.
