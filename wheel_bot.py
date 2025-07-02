#!/usr/bin/env python3
"""
Minimal Options Wheel bot for Alpaca.
Runs once per invocation – perfect for GitHub Actions cron.
Feel free to expand the selection logic; this is just a safe stub.
"""
import os, datetime as dt, pytz, math
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce, OptionClass
from alpaca.data.timeframe import TimeFrame
from alpaca.data.historical import StockHistoricalDataClient

# --- env vars ---
KEY  = os.getenv("ALPACA_KEY_ID")
SECRET = os.getenv("ALPACA_SECRET_KEY")
PAPER = os.getenv("ALPACA_PAPER", "true").lower() == "true"
SYMBOL = os.getenv("UNDERLYING", "SPY")          # the wheel underlying
DELTA  = float(os.getenv("TARGET_DELTA", "0.15"))  # ~15-delta strikes
SIZE   = int(os.getenv("CONTRACTS", "1"))

# --- clients ---
trade = TradingClient(KEY, SECRET, paper=PAPER)
data  = StockHistoricalDataClient()

def choose_expiry():
    """Pick the nearest weekly expiry ≥ 8 days out (stub)."""
    today = dt.date.today()
    # every Friday until 6 weeks out
    fridays = [today + dt.timedelta(days=i)
               for i in range(8, 42) if (today + dt.timedelta(days=i)).weekday()==4]
    return fridays[0]

def run_wheel():
    account = trade.get_account()
    pos     = trade.get_all_positions()
    has_shares = any(p.symbol == SYMBOL and int(p.qty) > 0 for p in pos)

    expiry = choose_expiry()

    if not has_shares:
        # SELL a cash-secured PUT
        print(f"No {SYMBOL} shares – selling CSP for {expiry}")
        trade.submit_option_order(
            underlying_symbol=SYMBOL,
            option_symbol=None,        # let Alpaca pick strike by delta
            option_class=OptionClass.PUT,
            contract_size=100,
            side=OrderSide.SELL,
            qty=SIZE,
            time_in_force=TimeInForce.DAY,
            delta=DELTA,
            expiry=expiry.isoformat()
        )
    else:
        # HAVE shares – SELL a covered CALL
        print(f"Holding {SYMBOL} – selling covered CALL for {expiry}")
        trade.submit_option_order(
            underlying_symbol=SYMBOL,
            option_symbol=None,
            option_class=OptionClass.CALL,
            contract_size=100,
            side=OrderSide.SELL,
            qty=SIZE,
            time_in_force=TimeInForce.DAY,
            delta=DELTA,
            expiry=expiry.isoformat()
        )

if __name__ == "__main__":
    run_wheel()
