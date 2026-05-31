"""StockScout Dashboard — Streamlit UI."""
import os
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from tools.market_data import fetch_price_history  # noqa: E402
from tools.signal_calculator import calculate_rsi  # noqa: E402
from agent.scoring_agent import score_universe  # noqa: E402
from config import UNIVERSE  # noqa: E402


st.set_page_config(page_title="StockScout", page_icon="📊", layout="wide")

st.title("📊 StockScout")
st.caption("AI agent that scores stocks daily across technical, momentum, fundamental, and sentiment signals")

# ---------- Sidebar ----------
with st.sidebar:
    st.header("Controls")
    if st.button("🔄 Run Daily Scoring", type="primary", use_container_width=True):
        with st.spinner("Scoring stocks... (1–3 minutes)"):
            results = score_universe(UNIVERSE)
            if results:
                df_new = pd.DataFrame(results)
                os.makedirs("data", exist_ok=True)
                df_new.to_csv("data/scores_latest.csv", index=False)
                st.success(f"Scored {len(results)} stocks")
                st.rerun()
            else:
                st.error("No results — check your connection.")
    st.divider()
    st.markdown(f"**LLM Provider:** `{os.getenv('LLM_PROVIDER', 'mock')}`")
    st.markdown(f"**Universe:** {len(UNIVERSE)} stocks")
    st.divider()
    st.markdown("**Weights**")
    st.text("Technical:    35%\nMomentum:     25%\nFundamental:  20%\nSentiment:    20%")

# ---------- Load scores ----------
if not os.path.exists("data/scores_latest.csv"):
    st.warning("No scores yet. Click **'Run Daily Scoring'** in the sidebar.")
    st.stop()

df = pd.read_csv("data/scores_latest.csv")
last_modified = datetime.fromtimestamp(os.path.getmtime("data/scores_latest.csv"))
st.caption(f"Last updated: {last_modified.strftime('%Y-%m-%d %H:%M:%S')}")

# ---------- Top metrics ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Stocks Scored", len(df))
c2.metric("Strong Buys", (df["recommendation"] == "STRONG BUY").sum())
c3.metric("Buys", (df["recommendation"] == "BUY").sum())
c4.metric("Sells", df["recommendation"].isin(["SELL", "STRONG SELL"]).sum())

st.divider()

# ---------- Filters ----------
col1, col2 = st.columns([2, 1])
with col1:
    rec_filter = st.multiselect(
        "Filter by recommendation",
        ["STRONG BUY", "BUY", "HOLD", "SELL", "STRONG SELL"],
        default=["STRONG BUY", "BUY", "HOLD", "SELL", "STRONG SELL"],
    )
with col2:
    sort_by = st.selectbox(
        "Sort by",
        ["composite_score", "technical_score", "momentum_score", "fundamental_score", "sentiment_score", "return_1m"],
        index=0,
    )

filtered = df[df["recommendation"].isin(rec_filter)].sort_values(sort_by, ascending=False)

# ---------- Ranked table ----------
st.subheader("📈 Ranked Stocks")

display_cols = [
    "ticker", "name", "current_price", "composite_score", "recommendation",
    "technical_score", "momentum_score", "fundamental_score", "sentiment_score",
    "rsi", "return_1m", "return_3m",
]
display_cols = [c for c in display_cols if c in filtered.columns]


def color_rec(val):
    colors = {
        "STRONG BUY": "background-color: #1a7f1a; color: white",
        "BUY": "background-color: #4caf50; color: white",
        "HOLD": "background-color: #ff9800; color: white",
        "SELL": "background-color: #f44336; color: white",
        "STRONG SELL": "background-color: #b71c1c; color: white",
    }
    return colors.get(val, "")

# Create display copy
display_df = filtered[display_cols].copy()

# Add colored indicator emojis (works reliably in Streamlit)
display_df["recommendation"] = display_df["recommendation"].map({
    "STRONG BUY": "🟢 STRONG BUY",
    "BUY": "🟩 BUY",
    "HOLD": "🟨 HOLD",
    "SELL": "🟥 SELL",
    "STRONG SELL": "🔴 STRONG SELL",
})

# Format numeric columns
for col in [
    "current_price",
    "composite_score",
    "technical_score",
    "momentum_score",
    "fundamental_score",
    "sentiment_score",
    "rsi",
]:
    if col in display_df.columns:
        display_df[col] = display_df[col].map(lambda x: f"{x:.1f}" if pd.notna(x) else "")

if "current_price" in display_df.columns:
    display_df["current_price"] = display_df["current_price"].astype(float).map(lambda x: f"{x:.2f}")

if "return_1m" in display_df.columns:
    display_df["return_1m"] = display_df["return_1m"].map(
        lambda x: f"{x:.2f}%" if pd.notna(x) else ""
    )

if "return_3m" in display_df.columns:
    display_df["return_3m"] = display_df["return_3m"].map(
        lambda x: f"{x:.2f}%" if pd.notna(x) else ""
    )

st.dataframe(
    display_df,
    use_container_width=True,
    height=500,
)
st.divider()

# ---------- Drill-down ----------
st.subheader("🔍 Detailed View")
if filtered.empty:
    st.warning("No stocks match the selected filters.")
    st.stop()

selected = st.selectbox(
    "Select a stock",
    filtered["ticker"].tolist()
)

if selected:
    row = filtered[filtered["ticker"] == selected].iloc[0]

    left, right = st.columns([1, 2])

    with left:
        st.markdown(f"### {row['name']}")
        st.caption(f"{row['ticker']}  •  {row.get('sector', 'N/A')}")
        st.metric("Current Price", f"{row['current_price']:.2f}")
        st.metric("Composite Score", f"{row['composite_score']:.1f}")
        st.markdown(f"#### Recommendation: **{row['recommendation']}**")

        st.markdown("**Score Breakdown**")
        st.progress(row["technical_score"] / 100, text=f"Technical: {row['technical_score']:.1f}")
        st.progress(row["momentum_score"] / 100, text=f"Momentum: {row['momentum_score']:.1f}")
        st.progress(row["fundamental_score"] / 100, text=f"Fundamental: {row['fundamental_score']:.1f}")
        st.progress(row["sentiment_score"] / 100, text=f"Sentiment: {row['sentiment_score']:.1f}")

        if pd.notna(row.get("reasoning")):
            st.markdown("**Reasoning**")
            st.info(row["reasoning"])
        if pd.notna(row.get("entry_signal")):
            st.markdown("**Entry Signal**")
            st.success(row["entry_signal"])
        if pd.notna(row.get("key_risks")):
            st.markdown("**Key Risks**")
            st.warning(row["key_risks"])

    with right:
        with st.spinner("Loading price chart..."):
            price_df = fetch_price_history(selected, period="6mo")

        if price_df is not None and not price_df.empty:
            close = price_df["Close"]
            sma_20 = close.rolling(20).mean()
            sma_50 = close.rolling(50).mean()
            rsi_series = calculate_rsi(close)

            fig = make_subplots(
                rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                row_heights=[0.7, 0.3],
                subplot_titles=("Price with Moving Averages", "RSI (14)"),
            )
            fig.add_trace(
                go.Candlestick(
                    x=price_df.index, open=price_df["Open"], high=price_df["High"],
                    low=price_df["Low"], close=price_df["Close"], name="Price",
                ), row=1, col=1,
            )
            fig.add_trace(go.Scatter(x=price_df.index, y=sma_20, name="SMA 20",
                                     line=dict(color="orange", width=1.5)), row=1, col=1)
            fig.add_trace(go.Scatter(x=price_df.index, y=sma_50, name="SMA 50",
                                     line=dict(color="blue", width=1.5)), row=1, col=1)
            fig.add_trace(go.Scatter(x=price_df.index, y=rsi_series, name="RSI",
                                     line=dict(color="purple")), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
            fig.update_layout(height=600, showlegend=True, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption("⚠️ **Disclaimer:** Educational project only. Not financial advice. Past performance does not guarantee future results.")
