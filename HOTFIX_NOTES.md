# Hotfix: no market data returned

This hotfix improves Streamlit Cloud behavior when a ticker returns no OHLCV data from yfinance.

Changes:
- Adds Stooq CSV fallback in `src/smart_money_agent/data_sources/market.py`.
- Adds graceful error handling in `streamlit_app.py`.
- Sets `Use SEC EDGAR` default to false for easier first-time testing.
- Adds 1mo lookback option for small/microcap tickers.
- Shows guidance instead of crashing when a ticker has no data.

Recommended first test tickers:
- AAPL
- NVDA
- TSLA
- PLTR
- IREN
- BURU
