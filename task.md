# Task: Optimize for Paid API & Expand Universe

User is on the paid Gemini API tier. We can reduce rate limit safeguards and expand the stock list to track broader market movements.

- [x] Reduce `time.sleep` in `trading.py` from 10s to 1s.
- [x] Add defensive/value stocks to `MARKET_UNIVERSE` in `config.py` (e.g., JPM, JNJ, WMT, PG, KO).
- [ ] Verify changes.
