
# Version 2.4 Notes

Added Insider Trading indicator layer:

- insider_net_buy_value_usd
- insider_buy_count
- insider_sell_count
- ceo_cfo_transaction_count
- ceo_cfo_net_buy_value_usd
- cluster_buying_count
- buy_size_vs_salary_ratio
- option_exercise_then_sell_count
- direct_open_market_buy_count
- direct_open_market_buy_value_usd

Dashboard changes:

- App title updated to v2.4
- Added `v2.4 Insider Trading Indicators` table
- Added Thai beginner explanations and summary
- Updated optional feed sample and schema

Scoring changes:

- insider_flow_score() now evaluates net buy/sell, buy/sell count, CEO/CFO activity,
  cluster buying, buy size vs salary, exercise-then-sell, and direct open-market buying.
