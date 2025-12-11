# Debugging AI Trading Errors

The user reported `HOLD: Error` for the last few stocks in the simulation loop. This is likely due to rate limiting (429) or transient API errors from the Gemini API, especially since they occur at the end of the list.

## Proposed Changes

### `trading.py`

#### [MODIFY] [trading.py](file:///c:/Users/Dario/source/repos/AiAgentForNews/trading.py)
1.  **Improve Error Logging**: Modify `ask_ai_for_decision` to capture the specific exception message and return it in the "reason" field. This allows the user (and us) to see *why* it failed (e.g., "429 Quota Exceeded").
2.  **Add Rate Limiting**: Insert a `time.sleep(2)` at the end of the `for symbol in MARKET_UNIVERSE:` loop in `run_simulation` to throttle requests.

## Verification Plan

### Automated Tests
- Run the simulation locally using `python -c "import trading; trading.run_simulation()"` and observe logs.
- We cannot easily simulate a 429 error, but we can verify that the new code structure runs without syntax errors and that the sleep delay works (by timing it).

### Manual Verification
- User will be asked to redeploy (`gcloud run deploy ...`).
- User can check the next scheduled report or trigger one manually (`/test-email`).
- User should verify that `INTC` and `PLTR` no longer show "Error", or if they do, the error message triggers debugging (e.g., "Quota exceeded") instead of generic "Error".
