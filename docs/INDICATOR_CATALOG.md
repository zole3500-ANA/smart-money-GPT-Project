# Smart Money Whale Agent v2 — Indicator Catalog

This catalog lists the indicators used or supported by the project. Indicators are grouped by the signal they are intended to capture.

## 1. Price / OHLCV base

| Indicator | Source | Meaning |
|---|---|---|
| Open | market OHLCV | Opening price |
| High | market OHLCV | Session high |
| Low | market OHLCV | Session low |
| Close | market OHLCV | Closing price |
| Volume | market OHLCV | Traded shares |
| DollarVolume | derived | Close × Volume |
| AvgDollarVolume20 | derived | 20-day average traded value |

## 2. Trend

| Indicator | Meaning |
|---|---|
| SMA10, SMA20, SMA50, SMA100, SMA200 | Simple moving averages |
| EMA8, EMA21, EMA50 | Exponential moving averages |
| TrendSlope20, TrendSlope50 | Slope proxy for moving averages |
| DistanceFromSMA20Pct, DistanceFromSMA50Pct, DistanceFromSMA200Pct | Price extension from key moving averages |
| GoldenCrossFlag | SMA50 crosses above SMA200 |
| DeathCrossFlag | SMA50 crosses below SMA200 |
| Breakout20DFlag | Close breaks above prior 20-day high |
| Breakdown20DFlag | Close breaks below prior 20-day low |

## 3. Momentum

| Indicator | Meaning |
|---|---|
| RSI14, RSI5 | Relative strength index |
| macd, macd_signal, macd_hist | MACD momentum set |
| ROC5, ROC20 | Rate of change |
| StochK14, StochD3 | Stochastic oscillator |

## 4. Volatility

| Indicator | Meaning |
|---|---|
| ATR14 | Average true range |
| ATRPercent | ATR14 / Close × 100 |
| TrueRangePct | Daily range as % of close |
| RealizedVol20 | Annualized 20-day realized volatility |
| BollingerWidthPct | Width of 20-day Bollinger band |

## 5. Volume / money flow / accumulation-distribution

| Indicator | Meaning |
|---|---|
| VWAP | Volume-weighted average price |
| VWAPDeviationPct | Close vs VWAP |
| OBV | On-balance volume |
| OBVTrend20 | 20-day OBV slope proxy |
| CMF20 | Chaikin money flow |
| MFI14 | Money flow index |
| ADL | Accumulation/distribution line |
| ADLTrend20 | 20-day ADL slope proxy |
| VPT | Volume price trend |
| VPTTrend20 | 20-day VPT slope proxy |
| EaseOfMovement14 | Ease of movement |
| CloseLocationValue | Close location in daily range |
| RelativeVolume30 | Current volume / 30-day average volume |
| VolumeZ | 30-day volume z-score |
| UpDownVolumeRatio20 | 20-day up-volume / down-volume ratio |
| FloatRotationProxy | Current volume / 60-day average volume |
| AccumulationDayFlag | Up day > 1.5% with higher volume |
| AccumulationDayCount25 | 25-day accumulation-day count |
| DistributionDayFlag | Down day < -1.5% with higher volume |
| DistributionDayCount25 | 25-day distribution-day count |
| PocketPivotProxy | Close above SMA10 with positive return and high 10-day volume |

## 6. Gap / tape reading / price structure

| Indicator | Meaning |
|---|---|
| GapPct | Open vs prior close |
| Return1D, Return5D, Return20D | Recent returns |
| IntradayReturnPct | Close vs open |
| HighLowRangePct | High/low range |
| CloseToHighPct | Close distance from high |
| CloseToLowPct | Close distance from low |
| OpeningRangeBreakoutProxy | Close above prior high with elevated volume |
| High52W, Low52W | Rolling 52-week structure |
| DistanceFrom52WHighPct | Distance from 52-week high |
| DistanceFrom52WLowPct | Distance from 52-week low |

## 7. Relative strength

| Indicator | Meaning |
|---|---|
| RS_SPY_Ratio | Stock / SPY price ratio |
| RS_SPY_Trend20 | 20-day slope proxy of stock/SPY ratio |
| RS_SPY_Return20DSpread | 20-day return spread vs SPY |
| RS_SPY_Return60DSpread | 60-day return spread vs SPY |
| RS_QQQ_Ratio | Stock / QQQ price ratio |
| RS_QQQ_Trend20 | 20-day slope proxy of stock/QQQ ratio |
| RS_QQQ_Return20DSpread | 20-day return spread vs QQQ |
| RS_QQQ_Return60DSpread | 60-day return spread vs QQQ |

## 8. SEC fundamentals and filings

| Indicator | Meaning |
|---|---|
| revenue_growth | SEC company-facts based revenue growth proxy |
| net_margin | SEC company-facts based net margin proxy |
| debt_to_assets | SEC company-facts based balance-sheet risk proxy |
| recent_filings | Recent 10-K, 10-Q, 8-K, S-1, S-3, 13D/G, Form 4 metadata |

## 9. FINRA daily short-volume pressure

| Indicator | Meaning |
|---|---|
| short_ratio | Daily short volume / total volume, if FINRA date is supplied |

## 10. Optional paid/third-party feed indicators

These are not fabricated. They are scored only when the user supplies a JSON file in `data/optional_feeds/{TICKER}.json`.

### Options flow

| Indicator | Meaning |
|---|---|
| unusual_options_volume_ratio | Options volume compared with normal baseline |
| call_put_volume_ratio | Call volume / put volume |
| put_call_ratio | Put volume / call volume |
| sweep_premium_usd | Premium from sweep orders |
| block_premium_usd | Premium from block trades |
| net_call_premium_usd | Net bullish call premium |
| net_put_premium_usd | Net bearish/hedge put premium |
| otm_call_share | Share of out-of-the-money call activity |
| iv_rank | Implied volatility rank |
| gamma_exposure_usd | Dealer gamma exposure estimate |

### Institutional / 13F

| Indicator | Meaning |
|---|---|
| thirteen_f_net_shares_change_pct | Net institutional holdings change |
| new_institutional_positions | New institutional holders |
| increased_positions | Holders that increased position |
| decreased_positions | Holders that decreased position |
| sold_out_positions | Holders that fully exited |
| institutional_ownership_pct | Institutional ownership share |
| top10_holder_concentration_pct | Concentration among top holders |

### Insider

| Indicator | Meaning |
|---|---|
| insider_net_buy_usd | Insider open-market net buying |
| open_market_buy_count_90d | Insider open-market buy count |
| open_market_sell_count_90d | Insider open-market sell count |
| cluster_buying_flag | Multiple insiders buying |
| ceo_cfo_buy_flag | CEO/CFO purchase signal |

### Dark pool / blocks

| Indicator | Meaning |
|---|---|
| dark_pool_volume_ratio | Off-exchange/dark pool share |
| large_block_trade_count | Large block trade count |
| block_price_vs_vwap_pct | Block price compared with VWAP |
| dark_pool_net_bias | Net buy/sell bias if provider supplies it |

### Short interest / squeeze

| Indicator | Meaning |
|---|---|
| short_interest_pct_float | Short interest as % of float |
| days_to_cover | Short interest / average daily volume |
| borrow_fee_rate_pct | Stock borrow fee |
| shares_available_to_borrow | Shares available for borrowing |
| short_interest_change_pct | Change in short interest |
| fails_to_deliver_value_usd | Fails-to-deliver value proxy |

### Sentiment and catalyst

| Indicator | Meaning |
|---|---|
| news_sentiment_score | News sentiment, usually -1 to +1 |
| social_sentiment_score | Social sentiment, usually -1 to +1 |
| mention_volume_zscore | Social/news mention spike |
| google_trends_zscore | Search-interest spike |
| analyst_revision_score | Analyst revision direction |
| days_to_earnings | Days until next earnings |
| earnings_surprise_pct | Latest earnings surprise |
| guidance_revision_score | Guidance change direction |
| offering_risk_flag | Dilution/offering risk |
| lawsuit_risk_flag | Legal risk |
| ma_rumor_flag | M&A catalyst flag |

## Component scoring weights in v2

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

## Interpretation

- 65–100 = Bullish
- 36–64 = Neutral
- 0–35 = Bearish

The score is a research signal, not a guarantee. One-day forecasts are especially noisy, so the forecast module intentionally caps certainty.
