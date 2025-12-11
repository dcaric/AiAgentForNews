import os
import json
import time
from datetime import datetime, date, timedelta
from google.cloud import storage
import google.generativeai as genai

# Alpaca & Gemini Imports
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.historical.news import NewsClient
from alpaca.data.requests import StockSnapshotRequest, NewsRequest
from alpaca.trading.requests import LimitOrderRequest, MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

# --- 2. CONFIGURATION ---

# A. Connect to Google Cloud Storage
BUCKET_NAME = os.environ.get("BUCKET_NAME")
STATE_FILE_NAME = 'portfolio_ai_state.json'

# B. Simulation Settings
STARTING_CASH = 1000.0
# MARKET_UNIVERSE imported from config
from config import MARKET_UNIVERSE 

# C. Load API Keys
ALPACA_KEY = os.environ.get('ALPACA_API_KEY')
ALPACA_SECRET = os.environ.get('ALPACA_SECRET_KEY')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')

if not all([ALPACA_KEY, ALPACA_SECRET, GEMINI_KEY]):
    print("⚠️  Warning: One or more API keys are missing (ALPACA_API_KEY, ALPACA_SECRET_KEY, GEMINI_API_KEY). Script may fail.")

# D. Initialize Alpaca
# Only initialize if keys are present to avoid immediate crash on import/run if just testing
if ALPACA_KEY and ALPACA_SECRET:
    trading_client = TradingClient(ALPACA_KEY, ALPACA_SECRET, paper=True)
    data_client = StockHistoricalDataClient(ALPACA_KEY, ALPACA_SECRET)
    news_client = NewsClient(ALPACA_KEY, ALPACA_SECRET)
else:
    trading_client = None
    data_client = None
    news_client = None

# --- 3. AI BRAIN SETUP ---

def configure_ai(log_func=print):
    if not GEMINI_KEY:
        return None
    
    genai.configure(api_key=GEMINI_KEY)
    possible_models = ['gemini-2.0-flash-exp', 'gemini-2.0-flash', 'gemini-1.5-flash']
    
    log_func("🔌 Connecting to AI Brain...")
    for model_name in possible_models:
        try:
            model = genai.GenerativeModel(model_name)
            model.generate_content("Ping")
            log_func(f"   ✅ AI Connected: Using '{model_name}'")
            return model
        except:
            continue
    raise Exception("❌ No Gemini models available.")

# We defer initialization of ai_model to inside run_simulation or global scope with a default print
ai_model = None 

# --- 4. CORE FUNCTIONS ---

def get_bucket():
    if not BUCKET_NAME:
        raise ValueError("BUCKET_NAME environment variable not set.")
    storage_client = storage.Client()
    return storage_client.bucket(BUCKET_NAME)

def init_state(log_func=print):
    try:
        bucket = get_bucket()
        blob = bucket.blob(STATE_FILE_NAME)
        
        if blob.exists():
            log_func(f"   📂 Loading state from GCS: gs://{BUCKET_NAME}/{STATE_FILE_NAME}")
            content = blob.download_as_text()
            return json.loads(content)
        else:
            log_func(f"   ✨ Creating new state in GCS: gs://{BUCKET_NAME}/{STATE_FILE_NAME}")
            new_state = {"start_date": str(date.today()), "cash": STARTING_CASH, "portfolio": {}, "history": []}
            save_state(new_state)
            return new_state
    except Exception as e:
        log_func(f"   ❌ Error initializing state: {e}")
        # Fallback to ephemeral state if GCS fails
        return {"start_date": str(date.today()), "cash": STARTING_CASH, "portfolio": {}, "history": []}

def save_state(state):
    try:
        bucket = get_bucket()
        blob = bucket.blob(STATE_FILE_NAME)
        blob.upload_from_string(json.dumps(state, indent=4))
        # print("   💾 State saved to GCS.")
    except Exception as e:
        print(f"   ❌ Error saving state to GCS: {e}")

def get_market_news(symbol):
    if not news_client: return []
    try:
        req = NewsRequest(symbols=symbol, start=datetime.now() - timedelta(hours=24), limit=3)
        return [n.headline for n in news_client.get_news(req).news]
    except: return []

def ask_ai_for_decision(symbol, price, pct_change, news_headlines, market_context=None, portfolio_context=None, model=None):
    if not model:
        return {"decision": "HOLD", "reason": "AI not connected"}

    # FALLBACK: If no news, explicit instruction to use Technicals
    if news_headlines:
        news_text = "\n".join([f"- {h}" for h in news_headlines])
    else:
        news_text = "NO SPECIFIC COMPANY NEWS FOUND."
    
    # Format World Context
    world_context_text = f"Global Market Context:\n{market_context}" if market_context else "No global context provided."

    # Format Portfolio Context
    if portfolio_context and portfolio_context.get('qty', 0) > 0:
        avg_price = portfolio_context.get('avg_price', 0)
        gain_pct = ((price - avg_price) / avg_price) * 100 if avg_price > 0 else 0
        portfolio_text = f"    WE OWN THIS STOCK: {portfolio_context['qty']} shares @ ${avg_price:.2f} (Current Gain: {gain_pct:+.2f}%)"
    else:
        portfolio_text = "    WE DO NOT OWN THIS STOCK."

    prompt = f"""
    Act as an Aggressive Day Trader. Manage a $1000 portfolio.
    
    STOCK: {symbol}
    PRICE: ${price:.2f}
    CHANGE (24H): {pct_change:.2f}%
    POSITIONS:
    {portfolio_text}
    
    COMPANY NEWS:
    {news_text}

    WORLD CONTEXT (Politics, Macroeconomics, Wars, Supply Chain):
    {world_context_text}
    
    STRATEGY RULES:
    1. ANALYZE GLOBAL IMPACT & NEWS: Are there major headwinds? If NEWS is NEGATIVE, SELL/AVOID.
    2. TAKE PROFIT: If we own the stock AND price is > 5% above Avg Entry, SELL (Lock in gains).
    3. STOP LOSS: If we own the stock AND price is < 5% below Avg Entry, SELL (Stop the bleeding).
    4. DIP BUY: If we DO NOT own it: Price down > 2% (Overreaction) AND News is NOT Negative -> BUY.
    5. MOMENTUM: If we DO NOT own it: Price up > 3% (FOMO) -> BUY.
    6. HOLD: If none of the above trigger, HOLD.
    
    Output strictly valid JSON (Example):
    {{ "decision": "HOLD", "reason": "Price is flat, no significant news." }}
    """
    
    try:
        config = genai.types.GenerationConfig(temperature=0.2, response_mime_type="application/json")
        response = model.generate_content(prompt, generation_config=config)
        return json.loads(response.text)
    except:
        return {"decision": "HOLD", "reason": "Error"}

# --- 5. MAIN SIMULATION LOOP ---

def run_simulation(return_logs=False, market_context=None):
    """
    Runs the simulation. 
    If return_logs=True, returns a string containing the output log.
    Otherwise, prints to stdout and returns None.
    """
    logs = []
    
    def log(message):
        if return_logs:
            logs.append(str(message))
        else:
            print(message)

        if return_logs: return "\n".join(logs), []
        return

    # Initialize AI (if not already done globally, ensuring we use local log)
    global ai_model
    if not ai_model:
        ai_model = configure_ai(log_func=log)

    state = init_state(log_func=log)
    if "equity_history" not in state:
        state["equity_history"] = []

    # CHECK MARKET HOURS
    market_open = True
    try:
        clock = trading_client.get_clock()
        if not clock.is_open:
            market_open = False
            log("🚫 Market is CLOSED. Running in Read-Only Mode (No AI/Trading).")
    except Exception as e:
        log(f"⚠️ Failed to check market hours: {e}. Proceeding with caution...")

    log(f"\n💼 PORTFOLIO: ${state['cash']:.2f} Cash | Holdings: {list(state['portfolio'].keys())}")
    
    log("   📡 Fetching Real-Time Data...")
    try:
        snap = data_client.get_stock_snapshot(StockSnapshotRequest(symbol_or_symbols=MARKET_UNIVERSE))
    except Exception as e:
        log(f"   ❌ Market Data Error: {e}")
        if return_logs: return "\n".join(logs), []
        return

    current_prices = {}

    for symbol in MARKET_UNIVERSE:
        if symbol not in snap: continue
        
        data = snap[symbol]
        if not data.latest_trade or not data.previous_daily_bar: continue
        
        price = data.latest_trade.price
        current_prices[symbol] = price # Store for equity calc
        
        prev = data.previous_daily_bar.close
        if prev == 0: continue
        change_pct = ((price - prev) / prev) * 100
        
        qty_owned = state["portfolio"].get(symbol, {}).get("qty", 0)

        # Filter: Only act if Owned OR Volatile (>1.5%)
        # For simulation purposes/testing, we might want to relax this or ensure we see output
        if (qty_owned > 0) or (abs(change_pct) > 1.5):
            log(f"\n   🔍 {symbol}: ${price:.2f} ({change_pct:+.2f}%)")
            
            # SKIPPING AI/TRADING IF MARKET CLOSED
            if not market_open:
                 continue

            headlines = get_market_news(symbol)
            if headlines: log(f"      📰 News: {headlines[0][:60]}...")
            
            # Get portfolio context for this symbol
            portfolio_ctx = state["portfolio"].get(symbol, {})
            
            # Debug Log for Gain %
            if portfolio_ctx.get("qty", 0) > 0:
                avg = portfolio_ctx.get("avg_price", 0)
                if avg > 0:
                    gain = ((price - avg) / avg) * 100
                    log(f"      💰 Position Gain/Loss: {gain:+.2f}% (Entry: ${avg:.2f})")
 
            ai_result = ask_ai_for_decision(symbol, price, change_pct, headlines, market_context=market_context, portfolio_context=portfolio_ctx, model=ai_model)
            decision = ai_result.get("decision", "HOLD").upper()
            reason = ai_result.get("reason", "N/A")
            
            log(f"      🤖 {decision}: {reason}")
            
            # --- EXECUTE TRADE ---
            
            # 1. BUY LOGIC
            if decision == "BUY":
                # CHECK FOR WASH TRADE (Cooldown Rule)
                today_str = str(date.today())
                # Use current system date for simplicity in simulation, 
                # but ideally should use clock.timestamp date for live trading across timezones.
                was_sold_today = any(f"{today_str}: SOLD {symbol}" in entry for entry in state["history"])
                
                if was_sold_today:
                    log(f"      ⚠️ SKIPPED BUY: Sold {symbol} today (Wash Trade Prevention)")
                elif qty_owned == 0:
                    # Calculate Quantity (Max 25% of cash)
                    invest_amount = state["cash"] * 0.25
                    
                    # FRACTIONAL SHARES: Allow buying if we have at least $10 to invest
                    if invest_amount >= 10.0:
                        qty_to_buy = round(invest_amount / price, 4)
                        
                        try:
                            # Use MARKET order for fractional shares
                            order_data = MarketOrderRequest(
                                symbol=symbol,
                                qty=qty_to_buy,
                                side=OrderSide.BUY,
                                time_in_force=TimeInForce.DAY
                            )
                            trading_client.submit_order(order_data)
                            
                            # Update State (Estimate cost at current price since it's market order)
                            cost = qty_to_buy * price
                            state["cash"] -= cost
                            state["portfolio"][symbol] = {"qty": qty_to_buy, "avg_price": price}
                            state["history"].append(f"{date.today()}: BOUGHT {qty_to_buy} {symbol}")
                            save_state(state)
                            log(f"      ✅ BOUGHT {qty_to_buy} {symbol} (Market Order)")
                        except Exception as e:
                            log(f"      ❌ Buy Failed: {e}")
                    else:
                        log(f"      ⚠️ SKIPPED BUY: Insufficient funds (${invest_amount:.2f}) for minimum trade")
                else:
                     log(f"      ⚠️ SKIPPED BUY: Already own {qty_owned} shares (Wait for sell signal)")

            # 2. SELL LOGIC
            elif decision == "SELL":
                if qty_owned > 0:
                    try:
                        # Use MARKET order to clear position (supports fractional)
                        order_data = MarketOrderRequest(
                            symbol=symbol,
                            qty=qty_owned,
                            side=OrderSide.SELL,
                            time_in_force=TimeInForce.DAY
                        )
                        trading_client.submit_order(order_data)
                        
                        # Update State
                        revenue = qty_owned * price
                        state["cash"] += revenue
                        del state["portfolio"][symbol]
                        state["history"].append(f"{date.today()}: SOLD {symbol}")
                        save_state(state)
                        log(f"      🚨 SOLD {qty_owned} {symbol} (Market Order)")
                    except Exception as e:
                        log(f"      ❌ Sell Failed: {e}")
                else:
                    log(f"      ⚠️ SKIPPED SELL: No position to sell")

    # --- CALCULATE TOTAL EQUITY ---
    holdings_value = 0.0
    for symbol, position in state["portfolio"].items():
        # Use current price if available, else fallback to avg_price (last known)
        price = current_prices.get(symbol, position.get("avg_price", 0))
        holdings_value += position.get("qty", 0) * price
    
    total_equity = state["cash"] + holdings_value
    
    # Update Equity History
    today_str = str(date.today())
    # Check if entry for today exists
    updated_history = False
    for entry in state["equity_history"]:
        if entry["date"] == today_str:
            entry["total"] = total_equity
            updated_history = True
            break
    if not updated_history:
        state["equity_history"].append({"date": today_str, "total": total_equity})
    
    save_state(state)

    log("\n--- 🏁 SCAN COMPLETE ---")
    log(f"💵 New Cash Balance: ${state['cash']:.2f}")
    log(f"💰 Total Equity: ${total_equity:.2f}")

    if return_logs:
        return "\n".join(logs), state

if __name__ == "__main__":
    run_simulation(return_logs=False)
