# Smart Money Whale Agent v3.0.2 — US Stock Indicator Analysis

Agent สำหรับวิเคราะห์หุ้นอเมริกาโดยเน้น **วาฬ / Smart Money / Institutional behavior** พร้อม pipeline แบบค้นข้อมูล → ตรวจสอบข้อมูล → วิเคราะห์ → สังเคราะห์คะแนน → วิเคราะห์หลายมุมมอง → forecast วันถัดไป

> Research only. This project is not financial advice. Always verify original filings, market data, liquidity, and risk before making decisions.











## What v3.0 adds

v3.0 เป็นการ **รีดีไซน์หน้าตา Dashboard ใหม่ทั้งหมด** ให้ใช้งานง่ายขึ้น:

- เพิ่ม **Hero Header** และสรุปภาพรวมบนหน้าแรก
- จัดหน้าใหม่เป็น **Tabs**
  - Overview
  - Key Indicators
  - Smart Money Tables
  - Beginner Summary
- Sidebar ใหม่ อ่านง่ายขึ้น แยกเป็นหมวดชัดเจน
- เพิ่มการ์ดสรุปแบบอ่านง่าย และปรับธีมให้ดูทันสมัย
- Metric cards, tabs และปุ่มถูกตกแต่งใหม่ให้ใช้งานง่ายขึ้น
- ลดความยาวของหน้า ทำให้ไม่ต้องเลื่อนลงยาวมากเหมือนเดิม

## What v2.9 adds

v2.9 ปรับหน้า Dashboard ให้เหมาะกับผู้ใช้งานทั่วไปมากขึ้น:

- ไม่แสดงหัวข้อ `Raw JSON` บนหน้า Streamlit แล้ว
- เหลือเฉพาะตารางวิเคราะห์, สรุปผล, กราฟ, คะแนน และคำแปลผลที่อ่านง่าย
- ข้อมูล JSON ยังอยู่ใน backend/report object สำหรับนักพัฒนาที่ต้องการ export ต่อ แต่ไม่แสดงบนหน้าเว็บหลัก

## What v2.8 adds

v2.8 เพิ่ม **No API Key Public/Proxy Mode + Confidence Verification**

- เปิดใช้ `Use free public sources / No API key` ใน Streamlit sidebar
- ดึงข้อมูลเสริมเท่าที่หาได้จากแหล่ง public/proxy:
  - Options chain proxy จาก public option chain ผ่าน yfinance
  - Insider trading จาก SEC Form 4 XML บน EDGAR
  - Institutional ownership proxy จาก public holders snapshot ถ้ามี
  - Dark pool/off-exchange proxy จาก FINRA daily short sale volume files
- ทุกตาราง optional feed จะแสดง:
  - แหล่งข้อมูล
  - ความมั่นใจของข้อมูล
  - ความสดของข้อมูล
  - ข้อจำกัด/หมายเหตุการทวนสอบ
- ถ้าหาข้อมูลกลุ่มใดไม่ได้เลย ระบบจะไม่แสดงตารางกลุ่มนั้น และจะแสดงรายชื่อใน “ตารางที่ถูกซ่อน”

## What v2.7 adds

v2.7 ปรับการแสดงผลตารางใหม่ให้อ่านง่ายขึ้น:

- เปลี่ยนจากตารางแบบเลื่อนขวา เป็น **ตาราง HTML แบบเต็มความกว้าง**
- **ตัดคำและขึ้นบรรทัดใหม่อัตโนมัติ** ในทุกคอลัมน์
- เปลี่ยนสีตัวอักษรให้ **เข้มและอ่านง่าย** ไม่กลืนกับพื้นหลัง
- คงระบบสีสถานะเดิม: 🟢 บวก / 🟡 กลาง / 🔴 ลบ
- แสดง badge สถานะชัดเจนสำหรับมือใหม่

## What v2.6 adds

v2.6 เพิ่ม **สัญลักษณ์และสีในทุกตารางแปลผล** เพื่อให้มือใหม่อ่านง่ายขึ้น:

| สัญลักษณ์ | สี | ความหมาย |
|---|---|---|
| 🟢 | เขียว | บวก / น่าสนใจ / มีแรงสนับสนุน |
| 🟡 | เหลือง | กลาง ๆ / รอดู / ยังไม่ชัด |
| 🔴 | แดง | ลบ / ต้องระวัง / มีแรงกดดัน |

ตารางที่อัปเดต:
- Component Scores
- Key Indicators
- Accumulation / Distribution
- Options Flow
- Insider Trading
- Institutional / Whale Ownership
- Dark Pool / Off-exchange

## What v2.5 adds

v2.5 เพิ่มตาราง **Options Flow Indicators** สำหรับจับวาฬระยะสั้นจาก optional feed:

| Indicator | ความหมาย | การตีความ |
|---|---|---|
| Unusual Options Volume | Volume options สูงผิดปกติ | มีคน bet ใหญ่ |
| Call Volume | ปริมาณซื้อขาย Call | มองขึ้น |
| Put Volume | ปริมาณซื้อขาย Put | มองลงหรือ hedge |
| Call/Put Volume Ratio | Call เทียบ Put | สูง = bullish sentiment |
| Put/Call Ratio | Put เทียบ Call | สูง = fear หรือ hedge |
| Options Volume / Open Interest | Volume เทียบ OI | สูง = มีสถานะใหม่ |
| Sweep Orders | คำสั่งไล่ซื้อหลายตลาด | วาฬเร่งเข้า |
| Block Trades | รายการใหญ่ | เงินก้อนใหญ่ |
| Premium Paid | มูลค่า options ที่จ่าย | ดูขนาดเงินจริง |
| Aggressor Side | ซื้อที่ ask หรือขายที่ bid | แยกว่าเปิด bullish/bearish |
| Near-term Expiry Flow | options ใกล้หมดอายุ | เก็งกำไรระยะสั้น |
| LEAPS Flow | options อายุยาว | มุมมองระยะยาว |
| OTM Call Buying | ซื้อ call นอกเงิน | เก็งขึ้นแรง |
| OTM Put Buying | ซื้อ put นอกเงิน | เก็งลงแรงหรือประกัน |
| Gamma Exposure | dealer gamma | คาดแรงเหวี่ยง |

Dashboard จะมีหัวข้อใหม่ `v2.5 Options Flow Indicators` พร้อมคำอธิบายภาษาไทยสำหรับมือใหม่

## What v2.4 adds

v2.4 เพิ่มตาราง **Insider Trading Indicators** สำหรับจับพฤติกรรมผู้บริหารซื้อ/ขายหุ้นจาก optional feed:

| Indicator | ความหมาย | การตีความ |
|---|---|---|
| Insider Net Buy/Sell | ผู้บริหารซื้อหรือขายสุทธิ | ซื้อ = บวก, ขาย = ต้องดูเหตุผล |
| Insider Buy Count | จำนวนรายการซื้อ | ซื้อหลายคนพร้อมกันน่าสนใจ |
| Insider Sell Count | จำนวนรายการขาย | ขายเยอะอาจกดดัน |
| CEO/CFO Transaction | ผู้บริหารระดับสูงซื้อขาย | น้ำหนักสูงกว่าคนทั่วไป |
| Cluster Buying | ผู้บริหารหลายคนซื้อพร้อมกัน | สัญญาณบวกแรง |
| Buy Size vs Salary | มูลค่าซื้อเทียบฐานะผู้บริหาร | ซื้อเยอะผิดปกติน่าสนใจ |
| Option Exercise then Sell | ใช้สิทธิแล้วขาย | อาจไม่ใช่ลบเสมอ |
| Direct Open Market Buy | ซื้อในตลาดจริง | สัญญาณบวกที่สุดในกลุ่ม insider |

Dashboard จะมีหัวข้อใหม่ `v2.4 Insider Trading Indicators` พร้อมคำอธิบายภาษาไทยสำหรับมือใหม่

## What v2.3 adds

v2.3 เพิ่มตาราง **Institutional / Whale Ownership Indicators** สำหรับจับการเคลื่อนไหวของกองทุนและผู้ถือหุ้นสถาบันจาก optional feed:

| Indicator | ความหมาย | สำคัญอย่างไร |
|---|---|---|
| 13F Net Institutional Flow | กองทุนเพิ่มหรือลดหุ้นสุทธิ | จับเงินสถาบัน |
| New Institutional Positions | มีกองทุนเปิดสถานะใหม่กี่ราย | ดูความสนใจใหม่ |
| Increased Positions | กองทุนเดิมซื้อเพิ่ม | สัญญาณสะสม |
| Decreased Positions | กองทุนเดิมลดพอร์ต | สัญญาณขาย |
| Sold Out Positions | กองทุนขายหมด | สัญญาณลบ |
| Top 10 Holder Concentration | ผู้ถือหุ้นใหญ่ถือรวมกี่ % | ดูความกระจุกตัว |
| Institutional Ownership % | สถาบันถือหุ้นกี่ % | หุ้นมีเจ้ามือสถาบันไหม |
| Quarter-over-quarter Holding Change | เปลี่ยนจากไตรมาสก่อนเท่าไร | ดู trend การสะสม |
| Whale Accumulation Score | คะแนนสะสมโดยรายใหญ่ | ใช้รวมเป็น smart money score |

Dashboard จะมีหัวข้อใหม่ `v2.3 Institutional / Whale Ownership Indicators` พร้อมคำอธิบายภาษาไทยสำหรับมือใหม่

## What v2.2 adds

v2.2 เพิ่มชุด **Dark Pool / Off-exchange Indicators** สำหรับจับการซื้อขายนอกกระดานปกติ โดยอ่านจาก optional feed JSON:

| Indicator | ความหมาย | ใช้วิเคราะห์ |
|---|---|---|
| Dark Pool Volume | Volume นอกตลาดหลัก | มีเงินใหญ่ซ่อนอยู่ไหม |
| Dark Pool % of Total Volume | สัดส่วน dark pool | สูงผิดปกติควรจับตา |
| Large Block Print | รายการซื้อขายก้อนใหญ่ | วาฬเข้าออก |
| Block Trade Price vs VWAP | block ซื้อแพงหรือถูกกว่า VWAP | ดู bias |
| Repeated Prints | มี block ซ้ำหลายครั้ง | อาจสะสมหรือกระจาย |
| Off-exchange Trend | dark pool เพิ่มต่อเนื่องไหม | ดูการเคลื่อนไหวเงียบ |
| Dark Pool Net Bias | ซื้อหรือขายมากกว่า | ใช้แยก buy bias / sell bias ถ้า provider มี aggressor side |

Dashboard จะมีตารางใหม่ชื่อ `v2.2 Dark Pool / Off-exchange Indicators` พร้อมคำแปลผลภาษาไทยสำหรับมือใหม่

ตัวอย่างไฟล์ optional feed:

```json
{
  "dark_pool": {
    "dark_pool_volume": 4200000,
    "total_volume": 10000000,
    "dark_pool_volume_ratio": 0.42,
    "large_block_trade_count": 14,
    "block_price_vs_vwap_pct": 0.35,
    "repeated_print_count": 6,
    "off_exchange_trend_5d": 6.5,
    "off_exchange_trend_20d": 12.0,
    "dark_pool_net_bias": 0.24
  }
}
```

## What v2.1 adds

v2.1 เพิ่มชุด **Accumulation / Distribution Indicators** ตามโจทย์สายวาฬ/Smart Money โดยเน้นจับการสะสมของ, การกระจายของ, volume สนับสนุนราคา และ divergence:

| Indicator | ความหมาย | การตีความ |
|---|---|---|
| Accumulation/Distribution Line (ADL) | เงินสะสมหรือไหลออก | ใช้จับ divergence |
| Money Flow Index (MFI) | RSI แบบรวม volume | เห็นแรงซื้อขายพร้อม volume |
| Volume Price Trend (VPT) | volume สนับสนุนราคาหรือไม่ | คล้าย OBV แต่ละเอียดกว่า |
| Ease of Movement (EMV) | ราคาขึ้นง่ายหรือลงง่าย | ดูแรงต้านของตลาด |
| Close Location Value (CLV) | ปิดใกล้ high หรือ low | ปิดใกล้ high = buyer control |
| Up/Down Volume Ratio | volume วันขึ้นเทียบวันลง | เงินเข้าหรือออก |
| Pocket Pivot | volume เข้าในจังหวะ breakout | สัญญาณสถาบันสะสม |
| Distribution Day Count | วันลงแรง volume สูง | ใช้จับกองทุนขาย |

Dashboard จะมีตารางแปลผลภาษาไทยสำหรับมือใหม่ในหัวข้อ `v2.1 Accumulation / Distribution Indicators`

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
