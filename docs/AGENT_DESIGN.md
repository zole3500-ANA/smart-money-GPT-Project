# Agent Design

## Pipeline

1. **Search / collect data**
   - Fetch OHLCV market data.
   - Fetch SPY/QQQ for relative strength.
   - Fetch SEC company facts and recent filing metadata when enabled.
   - Fetch FINRA daily short-sale volume when a trading date is supplied.
   - Load optional local JSON feeds for paid-data modules.

2. **Verify data**
   - Each source is assigned a freshness flag and confidence score.
   - Missing optional data does not stop the agent; it uses neutral score defaults.
   - Broad scans should normally disable SEC to avoid excessive requests.

3. **Analyze indicators**
   - Technical trend, momentum, volatility.
   - Money-flow and tape-reading indicators.
   - Relative strength against SPY/QQQ.
   - SEC fundamentals and filing-risk signals.
   - Optional options, dark-pool, institutional, insider, sentiment, and catalyst feeds.

4. **Synthesize scores**
   - 11 component scores are calculated.
   - Component scores are combined into a composite score.
   - Composite label: Bullish, Neutral, Bearish.

5. **Three-view analysis**
   - Price + fundamentals.
   - Psychology/sentiment.
   - Technical.
   - Smart Money / whale behavior.

6. **Next-day forecast**
   - Conservative probability from composite score.
   - ATR-based expected range.
   - Risk notes for volatility, extreme RSI, volume spikes, and gap risk.

## Score model

| Component | Default weight |
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

## Why optional paid feeds are neutral by default

Options sweeps, dark-pool bias, borrow fee, issuer-level 13F aggregation, and social/news sentiment often require licensed data. The project intentionally avoids fabricating those metrics. If the JSON file is absent, that component is scored as neutral rather than bullish or bearish.

## Broad US-stock scanning

Use:

```bash
python -m smart_money_agent.main --scan-all --scan-limit 500 --period 6mo --no-sec
```

This mode requires `POLYGON_API_KEY` to list active US common stocks. SEC calls should be disabled for broad scans unless a rate-limited queue is implemented.
