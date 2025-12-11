# Task: Fix API Rate Limiting

The user is encountering `429 Quota Exceeded` errors because the `gemini-2.0-flash-exp` model has a strict limit of 10 requests per minute (RPM).

- [x] Update `trading.py` to prioritize `gemini-1.5-flash` (higher rate limits).
- [x] Increase sleep delay in `run_simulation` from 2s to 12s (to allow 429 penalties to reset if hit, or just stay under 5 RPM to be safe across all tasks).
- [x] Implement BackgroundTasks in FastAPI to prevent 504 Gateway Timeouts.
- [x] Verify changes.
