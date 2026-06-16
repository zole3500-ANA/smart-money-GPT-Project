
# Version 2.8 Notes

Added No API Key Public/Proxy Mode with confidence verification.

Public/proxy sources:
- yfinance public option-chain proxy for Options Flow
- SEC EDGAR Form 4 XML parsing for Insider Trading
- public holders snapshot proxy for Institutional / Whale Ownership
- FINRA daily short-sale volume file for Dark Pool / Off-exchange proxy

Important:
- This is not a replacement for paid options flow or dark-pool feeds.
- Tables are omitted when no verifiable data is found.
- Each optional table shows source, confidence, freshness, and limitations.
