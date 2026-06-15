
# Accumulation / Distribution Indicators v2.1

ชุดนี้ใช้จับพฤติกรรมเงินใหญ่ในหุ้นอเมริกา โดยไม่ดูแค่ราคาขึ้นหรือลง แต่ดูว่า Volume และตำแหน่งราคาปิดสนับสนุนการเคลื่อนที่นั้นหรือไม่

| Indicator | Column | ความหมาย | การตีความ |
|---|---|---|---|
| Accumulation/Distribution Line | `ADL` | เงินสะสมหรือไหลออก | ใช้จับ divergence ระหว่างราคาและเงินสะสม |
| ADL Trend | `ADLTrend20` | แนวโน้ม ADL 20 วัน | บวก = สะสม, ลบ = กระจายของ |
| ADL Divergence | `ADLPriceDivergence20` | ราคาและ ADL สวนทางกัน | 1 = bullish divergence, -1 = bearish divergence |
| Money Flow Index | `MFI14` | RSI แบบรวม volume | >80 ร้อนแรง, <20 ถูกขายมาก |
| Volume Price Trend | `VPT` | Volume สนับสนุนราคาหรือไม่ | ใช้ร่วมกับ VPT trend |
| VPT Trend | `VPTTrend20` | แนวโน้ม VPT 20 วัน | บวก = volume หนุนราคา, ลบ = volume ไม่หนุน |
| VPT Divergence | `VPTPriceDivergence20` | ราคาและ VPT สวนทางกัน | 1 = bullish, -1 = bearish |
| Ease of Movement | `EaseOfMovement14` | ราคาขึ้นง่ายหรือลงง่าย | บวก = ขึ้นง่าย, ลบ = ลงง่าย/มีแรงต้าน |
| Close Location Value | `CloseLocationValue` | ปิดใกล้ high หรือ low | +1 ใกล้ high, -1 ใกล้ low |
| Up/Down Volume Ratio | `UpDownVolumeRatio20` | Volume วันขึ้นเทียบวันลง | >1 เงินเข้าเด่น, <1 เงินออกเด่น |
| Pocket Pivot | `PocketPivotProxy` | Volume เข้าในจังหวะราคาดี | 1 = เกิดสัญญาณวันนี้ |
| Pocket Pivot Count | `PocketPivotCount20` | จำนวน pocket pivot 20 วัน | มากขึ้น = มีร่องรอยสะสมหลายครั้ง |
| Distribution Day Count | `DistributionDayCount25` | วันลงแรง volume สูง | มาก = ระวังกองทุนขาย |
| Accumulation Day Count | `AccumulationDayCount25` | วันขึ้นแรง volume สูง | มาก = มีแรงซื้อสะสม |
| Net Accumulation Days | `NetAccumulationDays25` | วันสะสม - วันกระจายของ | บวก = สะสมมากกว่า, ลบ = ขายมากกว่า |

## Beginner interpretation

- ราคาเขียวอย่างเดียวไม่พอ ต้องดูว่า Volume สนับสนุนไหม
- ถ้าราคาลงแต่ ADL/VPT ไม่ลงตาม อาจเป็นการสะสมเงียบ
- ถ้าราคาขึ้นแต่ ADL/VPT ลง อาจเป็นขึ้นหลอกหรือ distribution
- ถ้ามี Distribution Day หลายวัน ให้ระวังแรงขายจากกองทุน
- Pocket Pivot เป็นสัญญาณเชิงบวกเมื่อ Volume เข้าในจังหวะราคาดี
