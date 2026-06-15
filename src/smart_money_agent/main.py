from __future__ import annotations

import argparse
from dotenv import load_dotenv

from .agent import SmartMoneyAgentConfig, SmartMoneyWhaleAgent
from .report import save_report, to_markdown
from .scanner import scan_all_us_stocks


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Smart Money Whale Agent for US stocks")
    parser.add_argument("--ticker", help="US stock ticker, e.g. AAPL, NVDA, IREN")
    parser.add_argument("--period", default="6mo", help="Data period, e.g. 3mo, 6mo, 1y")
    parser.add_argument("--finra-date", default=None, help="Last trading date for FINRA short volume, YYYYMMDD")
    parser.add_argument("--no-sec", action="store_true", help="Disable SEC EDGAR requests")
    parser.add_argument("--no-rs", action="store_true", help="Disable relative strength vs SPY/QQQ")
    parser.add_argument("--optional-feed-dir", default="data/optional_feeds", help="Directory for optional ticker JSON feeds")
    parser.add_argument("--output-dir", default="outputs", help="Output directory")

    parser.add_argument("--scan-all", action="store_true", help="Scan US common stocks using Polygon ticker list")
    parser.add_argument("--scan-limit", type=int, default=500, help="Max tickers to scan")
    parser.add_argument("--scan-workers", type=int, default=4, help="Parallel workers for scan")
    args = parser.parse_args()

    if args.scan_all:
        path = scan_all_us_stocks(
            limit=args.scan_limit,
            period=args.period,
            output_path=f"{args.output_dir}/us_stock_smart_money_ranking.csv",
            finra_date_yyyymmdd=args.finra_date,
            use_sec=not args.no_sec,
            max_workers=args.scan_workers,
        )
        print(f"Saved scan ranking: {path}")
        return

    if not args.ticker:
        parser.error("--ticker is required unless --scan-all is used")

    agent = SmartMoneyWhaleAgent(
        SmartMoneyAgentConfig(
            period=args.period,
            finra_date_yyyymmdd=args.finra_date,
            use_sec=not args.no_sec,
            use_relative_strength=not args.no_rs,
            optional_feed_dir=args.optional_feed_dir,
        )
    )
    report = agent.analyze(args.ticker)
    md_path, json_path = save_report(report, args.output_dir)
    print(to_markdown(report))
    print(f"\nSaved: {md_path}")
    print(f"Saved: {json_path}")


if __name__ == "__main__":
    main()
