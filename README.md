# Smart Money Whale Agent v2 — US Stock Indicator Analysis

Agent สำหรับวิเคราะห์หุ้นอเมริกาโดยเน้น **วาฬ / Smart Money / Institutional behavior** พร้อม pipeline แบบค้นข้อมูล → ตรวจสอบข้อมูล → วิเคราะห์ → สังเคราะห์คะแนน → วิเคราะห์หลายมุมมอง → forecast วันถัดไป

> Research only. This project is not financial advice. Always verify original filings, market data, liquidity, and risk before making decisions.

## What v2 adds

- 60+ built-in OHLCV/technical/money-flow indicators
- Smart Money scoring from VWAP, CMF, OBV, ADL, MFI, relative volume, Volume Z-score, accumulation/distribution day counts
- Relative strength vs SPY and QQQ
- Expanded score model with 11 components
- Optional local JSON feeds for paid/third-party data: options flow, 13F aggregation, insider, dark pool, exact short interest, sentiment, catalysts
- Batch scanner for US common stocks using Polygon ticker list
- CLI reports, JSON output, Markdown output, and Streamlit dashboard

## Data-source philosophy

The open-source version does not fabricate unavailable data.

Free/open modules:

- Market OHLCV: Polygon if `POLYGON_API_KEY` is set; yfinance fallback for experimentation
- SEC EDGAR: company facts and recent filings
- FINRA daily short-sale volume: enabled when a trading date is supplied

Optional paid/provider modules:

- Options sweeps / unusual options / block premium
- Dark pool / off-exchange block bias
- Full issuer-level 13F aggregation
- Exact short interest, borrow fee, shares available to borrow
- News/social sentiment and catalyst calendar

These optional feeds are loaded from local JSON files in `data/optional_feeds/{TICKER}.json`.

## Install

```bash
cd smart_money_agent
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
pip install -e .
```

## Environment

Copy `.env.example` to `.env`.

```bash
POLYGON_API_KEY=your_polygon_key_here
SEC_USER_AGENT="Your Name your.email@example.com"
```

`POLYGON_API_KEY` is optional for one-ticker experiments but required for full US-stock scans.

## Run one ticker

```bash
python -m smart_money_agent.main --ticker AAPL --period 6mo
```

Without SEC:

```bash
python -m smart_money_agent.main --ticker NVDA --period 1y --no-sec
```

With FINRA short-volume date:

```bash
python -m smart_money_agent.main --ticker IREN --period 6mo --finra-date 20260612
```

The tool saves:

```text
outputs/AAPL_report.md
outputs/AAPL_signal.json
```

## Run dashboard

```bash
streamlit run streamlit_app.py
```

## Scan US common stocks

Requires `POLYGON_API_KEY`.

```bash
python -m smart_money_agent.main --scan-all --scan-limit 500 --period 6mo --no-sec
```

Output:

```text
outputs/us_stock_smart_money_ranking.csv
```

SEC is disabled by default for broad scans in the helper because running SEC requests across thousands of tickers can hit fair-access limits. Use ticker-level analysis for deeper SEC review.

## Optional feed file

Create a file such as:

```text
data/optional_feeds/AAPL.json
```

Example schema is in:

```text
docs/OPTIONAL_FEED_SCHEMA.json
```

Minimal example:

```json
{
  "options_flow": {
    "unusual_options_volume_ratio": 2.4,
    "call_put_volume_ratio": 1.8,
    "net_call_premium_usd": 650000,
    "net_put_premium_usd": 120000,
    "iv_rank": 44
  },
  "institutional_flow": {
    "thirteen_f_net_shares_change_pct": 4.5,
    "increased_positions": 84,
    "decreased_positions": 52
  },
  "short_interest": {
    "short_interest_pct_float": 11.5,
    "days_to_cover": 3.2,
    "borrow_fee_rate_pct": 4.7
  }
}
```

If no optional feed exists, the corresponding score components use neutral defaults, usually 50.

## Score components

| Component | Weight |
|---|---:|
| Smart money flow | 25% |
| Technical trend | 18% |
| Options flow | 12% |
| Short pressure / squeeze | 10% |
| Fundamental quality | 10% |
| Institutional / 13F flow | 8% |
| Insider flow | 5% |
| Dark pool / block flow | 4% |
| Relative strength | 4% |
| Psychology / sentiment | 2% |
| Catalyst / filing risk | 2% |

Interpretation:

| Composite score | Label |
|---:|---|
| 65–100 | Bullish |
| 36–64 | Neutral |
| 0–35 | Bearish |

## Indicator catalog

Full indicator list:

```text
docs/INDICATOR_CATALOG.md
```

Key built-in indicators include:

- SMA10/20/50/100/200, EMA8/21/50
- RSI14, RSI5, MACD, ROC, Stochastic
- ATR, ATR%, realized volatility, Bollinger width
- VWAP deviation, OBV, CMF, MFI, ADL, VPT, EMV
- Relative volume, Volume Z-score, Up/Down volume ratio
- Accumulation day count, distribution day count, pocket pivot proxy
- Gap%, return 1D/5D/20D, close-location value
- 52-week distance, breakout/breakdown flags
- Relative strength spreads vs SPY and QQQ

## Project structure

```text
smart_money_agent/
├─ README.md
├─ requirements.txt
├─ pyproject.toml
├─ config.yaml
├─ streamlit_app.py
├─ data/optional_feeds/
├─ docs/
│  ├─ AGENT_DESIGN.md
│  ├─ INDICATOR_CATALOG.md
│  └─ OPTIONAL_FEED_SCHEMA.json
├─ src/smart_money_agent/
│  ├─ agent.py
│  ├─ alternative_data.py
│  ├─ indicators.py
│  ├─ scoring.py
│  ├─ prediction.py
│  ├─ report.py
│  ├─ scanner.py
│  └─ data_sources/
└─ tests/
```

## GitHub upload

```bash
git init
git add .
git commit -m "Add smart money whale agent v2"
git branch -M main
git remote add origin <your_repo_url>
git push -u origin main
```

## Important limitations

- One-day prediction is noisy and should be treated as a probabilistic research signal.
- FINRA daily short-volume is not the same as exchange-reported short interest.
- 13F data is delayed and does not show real-time institutional positions.
- Insider selling is not always bearish because it can be tax, diversification, or pre-planned selling.
- Options-flow and dark-pool feeds require careful provider-specific interpretation.
