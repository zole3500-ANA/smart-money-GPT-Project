
# Insider Trading Indicators v2.4

กลุ่มนี้ใช้จับพฤติกรรมผู้บริหารและ insider จากข้อมูล Form 4 หรือ insider transaction aggregator

| Indicator | JSON key | ความหมาย | การตีความ |
|---|---|---|---|
| Insider Net Buy/Sell | `insider_net_buy_value_usd` | ผู้บริหารซื้อหรือขายสุทธิ | ซื้อ = บวก, ขาย = ต้องดูเหตุผล |
| Insider Buy Count | `insider_buy_count` | จำนวนรายการซื้อ | ซื้อหลายคนพร้อมกันน่าสนใจ |
| Insider Sell Count | `insider_sell_count` | จำนวนรายการขาย | ขายเยอะอาจกดดัน |
| CEO/CFO Transaction | `ceo_cfo_transaction_count` | ผู้บริหารระดับสูงซื้อขาย | น้ำหนักสูงกว่าคนทั่วไป |
| CEO/CFO Net Buy/Sell | `ceo_cfo_net_buy_value_usd` | CEO/CFO ซื้อขายสุทธิ | ซื้อสุทธิมีน้ำหนักบวกสูง |
| Cluster Buying | `cluster_buying_count` | ผู้บริหารหลายคนซื้อพร้อมกัน | สัญญาณบวกแรง |
| Buy Size vs Salary | `buy_size_vs_salary_ratio` | มูลค่าซื้อเทียบฐานะผู้บริหาร | ซื้อเยอะผิดปกติน่าสนใจ |
| Option Exercise then Sell | `option_exercise_then_sell_count` | ใช้สิทธิแล้วขาย | อาจไม่ใช่ลบเสมอ |
| Direct Open Market Buy | `direct_open_market_buy_count` | ซื้อในตลาดจริง | สัญญาณบวกที่สุดในกลุ่ม insider |
| Direct Open Market Buy Value | `direct_open_market_buy_value_usd` | มูลค่าซื้อในตลาดจริง | ยิ่งมากยิ่งมีน้ำหนัก |

## Beginner interpretation

- Insider ซื้อสุทธิ = บวกกว่าขายสุทธิ
- CEO/CFO ซื้อเอง = น้ำหนักสูงกว่าผู้บริหารทั่วไป
- Cluster buying = หลายคนซื้อพร้อมกัน น่าสนใจกว่าคนเดียวซื้อ
- Direct open market buy = ซื้อด้วยเงินจริงในตลาด เป็นสัญญาณคุณภาพสูง
- Option exercise then sell = ไม่ควรตีความลบทันที เพราะอาจเกี่ยวกับค่าตอบแทน/ภาษี
