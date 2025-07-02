#!/usr/bin/env python3
"""
Minimal Options Wheel bot for Alpaca – one-shot per run.
"""
import os, datetime as dt
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce, OptionClass

KEY    = os.getenv("ALPACA_KEY_ID")
SECRET = os.getenv("ALPACA_SECRET_KEY")
PAPER  = os.getenv("ALPACA_PAPER", "true").lower() == "true"

SYMBOL = os.getenv("UNDERLYING", "SPY")
DELTA  = float(os.getenv("TARGET_DELTA", "0.15"))
SIZE   = int(os.getenv("CONTRACTS", "1"))

trade = TradingClient(KEY, SECRET, paper=PAPER)

def next_weekly_friday(start=dt.date.today(), min_days=8):
    for d in range(min_days, 42):
        day = start + dt.timedelta(days=d)
        if day.weekday() == 4:
            return day

def run():
    has_shares = any(p.symbol == SYMBOL and int(p.qty) > 0
                     for p in trade.get_all_positions())
    expiry = next_weekly_friday()

    order_args = dict(
        underlying_symbol = SYMBOL,
        qty              = SIZE,
        delta            = DELTA,
        expiry           = str(expiry),
        time_in_force    = TimeInForce.DAY,
    )

    if not has_shares:          # SELL cash-secured PUT
        print(f"No {SYMBOL} shares – selling CSP for {expiry}")
        trade.submit_option_order(option_class = OptionClass.PUT,
                                  side         = OrderSide.SELL,
                                  **order_args)
    else:                       # SELL covered CALL
        print(f"Holding shares – selling covered CALL for {expiry}")
        trade.submit_option_order(option_class = OptionClass.CALL,
                                  side         = OrderSide.SELL,
                                  **order_args)

if __name__ == "__main__":
    run()
