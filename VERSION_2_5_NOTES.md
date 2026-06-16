
# Version 2.5 Notes

Added Options Flow indicator layer:

- unusual_options_volume
- unusual_options_volume_z
- call_volume
- put_volume
- call_put_volume_ratio
- put_call_ratio
- options_volume_open_interest_ratio
- sweep_order_count
- sweep_premium_usd
- options_block_trade_count
- block_trade_premium_usd
- premium_paid_usd
- aggressor_side
- near_term_call_premium_usd
- near_term_put_premium_usd
- leaps_call_premium_usd
- leaps_put_premium_usd
- otm_call_premium_usd
- otm_put_premium_usd
- gamma_exposure
- gamma_exposure_pct_float
- bullish_premium_ratio

Dashboard changes:

- App title updated to v2.5
- Added `v2.5 Options Flow Indicators` table
- Added Thai beginner explanations and summary
- Updated optional feed sample and schema

Scoring changes:

- options_flow_score() now evaluates unusual volume, call/put, put/call, volume/OI,
  sweeps, blocks, premium paid, aggressor side, near-term flow, LEAPS, OTM flow,
  gamma exposure, and combination rules.
