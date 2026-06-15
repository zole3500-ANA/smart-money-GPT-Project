
# Version 2.2 Notes

Added Dark Pool / Off-exchange indicator layer:

- `dark_pool_volume`
- `dark_pool_volume_ratio`
- `dark_pool_pct_total_volume`
- `large_block_trade_count`
- `large_block_volume`
- `large_block_value_usd`
- `largest_block_value_usd`
- `block_price_vs_vwap_pct`
- `repeated_print_count`
- `repeated_print_ratio`
- `off_exchange_trend_5d`
- `off_exchange_trend_20d`
- `dark_pool_buy_volume`
- `dark_pool_sell_volume`
- `dark_pool_net_bias`

Dashboard changes:

- App title updated to v2.2
- Added `v2.2 Dark Pool / Off-exchange Indicators` table
- Added Thai beginner explanations for all dark-pool fields
- Added simple beginner summary for dark pool ratio, block vs VWAP, net bias, repeated prints, and off-exchange trend

Scoring changes:

- `dark_pool_flow_score()` now evaluates:
  - dark-pool participation
  - large block count/value
  - block price vs VWAP
  - repeated prints
  - off-exchange trend
  - net bias / aggressor-side data
- Default dark-pool score weight increased from 4% to 6%.
