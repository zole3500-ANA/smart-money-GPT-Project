
# Dark Pool / Off-exchange Indicators v2.2

กลุ่มนี้ใช้จับการซื้อขายนอกกระดานปกติ เช่น dark pool, off-exchange prints และ block trades

> หมายเหตุ: ข้อมูล dark pool คุณภาพสูงมักต้องใช้ผู้ให้บริการข้อมูลเสียเงิน จึงออกแบบเป็น optional feed ผ่าน JSON

| Indicator | Column / JSON key | ความหมาย | ใช้วิเคราะห์ |
|---|---|---|---|
| Dark Pool Volume | `dark_pool_volume` | Volume นอกตลาดหลัก | มีเงินใหญ่ซ่อนอยู่ไหม |
| Dark Pool % of Total Volume | `dark_pool_volume_ratio` หรือ `dark_pool_pct_total_volume` | สัดส่วน dark pool | สูงผิดปกติควรจับตา |
| Large Block Print | `large_block_trade_count` | รายการซื้อขายก้อนใหญ่ | วาฬเข้าออก |
| Large Block Volume | `large_block_volume` | จำนวนหุ้นจาก block trades | ขนาดการเคลื่อนไหว |
| Large Block Value | `large_block_value_usd` | มูลค่ารวมของ block trades | ขนาดเงินจริง |
| Largest Block Print | `largest_block_value_usd` | block trade ก้อนใหญ่ที่สุด | ดูรายการผิดปกติ |
| Block Trade Price vs VWAP | `block_price_vs_vwap_pct` | block ซื้อแพงหรือถูกกว่า VWAP | ดู bias |
| Repeated Prints | `repeated_print_count` | มี block ซ้ำหลายครั้ง | อาจสะสมหรือกระจาย |
| Repeated Print Ratio | `repeated_print_ratio` | repeated prints / block prints | ดู pattern ซ้ำ |
| Off-exchange Trend 5D | `off_exchange_trend_5d` | dark pool เพิ่มต่อเนื่องระยะสั้นไหม | ดูการเคลื่อนไหวเงียบ |
| Off-exchange Trend 20D | `off_exchange_trend_20d` | dark pool เพิ่มต่อเนื่องระยะกลางไหม | ดูการเปลี่ยนแปลงสะสม |
| Dark Pool Buy Volume | `dark_pool_buy_volume` | volume ฝั่งซื้อ ถ้ามี aggressor side | buy pressure |
| Dark Pool Sell Volume | `dark_pool_sell_volume` | volume ฝั่งขาย ถ้ามี aggressor side | sell pressure |
| Dark Pool Net Bias | `dark_pool_net_bias` | ซื้อหรือขายมากกว่า | บวก = buy bias, ลบ = sell bias |

## การอ่านแบบมือใหม่

- Dark pool ratio สูงอย่างเดียวไม่ใช่บวกเสมอ ต้องดู bias ด้วย
- Block price above VWAP = มีคนยอมซื้อแพงกว่า VWAP เป็นสัญญาณบวกกว่า
- Block price below VWAP = มีโอกาสเป็นแรงขายหรือ distribution
- Repeated prints หลายครั้ง = อาจเป็นการทยอยสะสมหรือทยอยขาย
- Off-exchange trend เพิ่มขึ้น = มีการเคลื่อนไหวเงียบมากขึ้น
- Net bias บวก = ฝั่งซื้อเด่นกว่า
- Net bias ลบ = ฝั่งขายเด่นกว่า

## Scoring logic

Dark pool score v2.2 ใช้ข้อมูลหลายตัวรวมกัน:

- สัดส่วน dark pool
- จำนวน/magnitude ของ block trades
- ราคา block เทียบ VWAP
- repeated print pattern
- off-exchange trend
- buy/sell net bias
- combination rules เช่น ratio สูง + block above VWAP + buy bias
