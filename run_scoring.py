"""CLI entrypoint — run the scoring pipeline and save to CSV."""
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from config import UNIVERSE  # noqa: E402
from agent.scoring_agent import score_universe  # noqa: E402


def main():
    print(f"\n{'='*60}")
    print(f"  StockScout — Daily Scoring Run")
    print(f"  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  LLM Provider: {os.getenv('LLM_PROVIDER', 'mock')}")
    print(f"  Universe size: {len(UNIVERSE)} stocks")
    print(f"{'='*60}\n")

    results = score_universe(UNIVERSE)
    if not results:
        print("\n✗ No results. Check your internet connection or tickers.")
        return

    df = pd.DataFrame(results)
    os.makedirs("data", exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    df.to_csv(f"data/scores_{date_str}.csv", index=False)
    df.to_csv("data/scores_latest.csv", index=False)

    print(f"\n{'='*60}")
    print(f"  ✓ Scored {len(results)} stocks")
    print(f"  ✓ Saved to data/scores_latest.csv")
    print(f"{'='*60}\n")

    print("TOP 5 BY SCORE:")
    for i, r in enumerate(results[:5], 1):
        print(f"  {i}. {r['ticker']:<18} {r['composite_score']:>6.1f}  [{r['recommendation']}]")

    print("\nBOTTOM 5 BY SCORE:")
    for i, r in enumerate(results[-5:], 1):
        print(f"  {i}. {r['ticker']:<18} {r['composite_score']:>6.1f}  [{r['recommendation']}]")

    print("\nRun the dashboard with:  streamlit run app.py\n")


if __name__ == "__main__":
    main()
