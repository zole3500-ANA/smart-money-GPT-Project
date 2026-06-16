
# Institutional / Whale Ownership Indicators v2.3

กลุ่มนี้ใช้จับการเคลื่อนไหวของกองทุน สถาบัน และผู้ถือหุ้นรายใหญ่ โดยเน้นข้อมูล 13F และ ownership aggregation

> หมายเหตุ: Form 13F เป็นข้อมูลรายไตรมาสและมีความล่าช้า จึงเหมาะกับการดู trend ไม่ใช่สัญญาณ intraday

| Indicator | JSON key | ความหมาย | สำคัญอย่างไร |
|---|---|---|---|
| 13F Net Institutional Flow | `net_institutional_flow_pct` | กองทุนเพิ่มหรือลดหุ้นสุทธิ | จับเงินสถาบัน |
| Net Institutional Flow Value | `net_institutional_flow_value_usd` | มูลค่าซื้อ/ขายสุทธิ | ดูขนาดเงินจริง |
| New Institutional Positions | `new_positions_count` | มีกองทุนเปิดสถานะใหม่กี่ราย | ดูความสนใจใหม่ |
| Increased Positions | `increased_positions_count` | กองทุนเดิมซื้อเพิ่ม | สัญญาณสะสม |
| Decreased Positions | `decreased_positions_count` | กองทุนเดิมลดพอร์ต | สัญญาณขาย |
| Sold Out Positions | `sold_out_positions_count` | กองทุนขายหมด | สัญญาณลบ |
| Top 10 Holder Concentration | `top10_holder_concentration_pct` | ผู้ถือหุ้นใหญ่ถือรวมกี่ % | ดูความกระจุกตัว |
| Institutional Ownership % | `institutional_ownership_pct` | สถาบันถือหุ้นกี่ % | หุ้นมีเจ้ามือสถาบันไหม |
| Quarter-over-quarter Holding Change | `qoq_holding_change_pct` | เปลี่ยนจากไตรมาสก่อนเท่าไร | ดู trend การสะสม |
| Whale Accumulation Score | `whale_accumulation_score` | คะแนนสะสมโดยรายใหญ่ | ใช้รวมเป็น smart money score |
