
# Options Flow Indicators v2.5

กลุ่มนี้สำคัญมากในการจับวาฬระยะสั้น โดยเน้นข้อมูลจาก options-flow provider เช่น unusual volume, sweeps, block trades, premium, aggressor side และ gamma

| Indicator | JSON key | ความหมาย | การตีความ |
|---|---|---|---|
| Unusual Options Volume | `unusual_options_volume` | Volume options สูงผิดปกติ | มีคน bet ใหญ่ |
| Call Volume | `call_volume` | ปริมาณซื้อขาย Call | มองขึ้น |
| Put Volume | `put_volume` | ปริมาณซื้อขาย Put | มองลงหรือ hedge |
| Call/Put Volume Ratio | `call_put_volume_ratio` | Call เทียบ Put | สูง = bullish sentiment |
| Put/Call Ratio | `put_call_ratio` | Put เทียบ Call | สูง = fear หรือ hedge |
| Options Volume / Open Interest | `options_volume_open_interest_ratio` | Volume เทียบ OI | สูง = มีสถานะใหม่ |
| Sweep Orders | `sweep_order_count` | คำสั่งไล่ซื้อหลายตลาด | วาฬเร่งเข้า |
| Block Trades | `options_block_trade_count` | รายการใหญ่ | เงินก้อนใหญ่ |
| Premium Paid | `premium_paid_usd` | มูลค่า options ที่จ่าย | ดูขนาดเงินจริง |
| Aggressor Side | `aggressor_side` | ซื้อที่ ask หรือขายที่ bid | แยกว่าเปิด bullish/bearish |
| Near-term Expiry Flow | `near_term_call_premium_usd`, `near_term_put_premium_usd` | options ใกล้หมดอายุ | เก็งกำไรระยะสั้น |
| LEAPS Flow | `leaps_call_premium_usd`, `leaps_put_premium_usd` | options อายุยาว | มุมมองระยะยาว |
| OTM Call Buying | `otm_call_premium_usd` | ซื้อ call นอกเงิน | เก็งขึ้นแรง |
| OTM Put Buying | `otm_put_premium_usd` | ซื้อ put นอกเงิน | เก็งลงแรงหรือประกัน |
| Gamma Exposure | `gamma_exposure` | dealer gamma | คาดแรงเหวี่ยง |

## Beginner interpretation

- Call/Put สูง = options sentiment เอน bullish
- Put/Call สูง = fear หรือ hedge เยอะ
- Volume/OI สูง = อาจมีการเปิดสถานะใหม่
- Sweep ที่ ask = วาฬเร่งซื้อ
- Sweep/Block premium สูง = เงินก้อนใหญ่
- OTM call สูง = เก็งขึ้นแรง
- OTM put สูง = เก็งลงแรงหรือประกันความเสี่ยง
- Gamma ลบ = ราคาอาจเหวี่ยงแรงขึ้น
