#!/usr/bin/env python3
"""
Aggressive Portfolio Simulation — Investment Daily
==================================================
High-risk paper simulation focused on maximizing upside with small capital.

Usage:
  python aggressive_sim.py            # print current P&L to console
  python aggressive_sim.py --init     # reset simulation state
  python aggressive_sim.py --snapshot # save daily equity point
"""

import json
import os
import sys
from datetime import date, datetime

import yfinance as yf

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(SCRIPT_DIR, "sim_portfolio_aggressive.json")
TOTAL_CAPITAL = 5_000.00
BENCHMARK = {"ticker": "BTC-USD", "entry_price": None}

# Aggressive assumptions (explicitly riskier than portfolio_sim.py)
MAX_POSITIONS = 10  # default; can be overridden via state["config"]["max_positions"]
MIN_TRADE_SIZE = 400.0
MAX_SINGLE_ALLOC_PCT = 0.70

# Fee model
SPOT_TRADE_FEE_RATE = 0.0010       # 0.10%
SPOT_SLIPPAGE_RATE = 0.0015        # 0.15%
OPTION_TRADE_FEE_RATE = 0.0060     # 0.60% (crypto options, taker-like)
OPTION_SLIPPAGE_RATE = 0.0030       # 0.30%


def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, default=str)


def get_price(ticker: str) -> float | None:
    try:
        hist = yf.Ticker(ticker).history(period="1d")
        if hist.empty:
            return None
        return float(hist["Close"].iloc[-1])
    except Exception:
        return None


def get_current_prices(tickers: list[str]) -> dict[str, float]:
    out: dict[str, float] = {}
    for t in tickers:
        p = get_price(t)
        if p and p > 0:
            out[t] = p
    return out


def init_simulation() -> dict:
    btc_price = get_price("BTC-USD") or 0.0
    state = {
        "initialized": datetime.now().isoformat(),
        "init_date": date.today().isoformat(),
        "total_capital": TOTAL_CAPITAL,
        "cash": TOTAL_CAPITAL,
        "positions": {},
        "fees_paid": 0.0,
        "trade_log": [],
        "snapshots": [],
        "config": {"max_positions": MAX_POSITIONS},
        "benchmark": {
            "ticker": "BTC-USD",
            "entry_price": btc_price if btc_price > 0 else None,
        },
    }
    save_state(state)
    return state


def _append_trade(state: dict, event: dict) -> None:
    event["timestamp"] = datetime.now().isoformat()
    log = state.setdefault("trade_log", [])
    log.append(event)
    state["trade_log"] = log[-300:]


def _signal_map(signals: list[dict]) -> dict[str, dict[str, list[dict]]]:
    mapped: dict[str, dict[str, list[dict]]] = {}
    for s in signals:
        t = str(s.get("ticker", "")).strip()
        if not t:
            continue
        side = str(s.get("direction", "")).upper()
        if t not in mapped:
            mapped[t] = {"bullish": [], "bearish": []}
        if side == "BULLISH":
            mapped[t]["bullish"].append(s)
        elif side == "BEARISH":
            mapped[t]["bearish"].append(s)
    return mapped


def _score(sig: dict) -> float:
    d5 = sig.get("backtest", {}).get("5d", {})
    conf = (sig.get("confidence") or 50) / 100
    wr = (d5.get("win_rate") or 50) / 100
    sharpe = min(abs(d5.get("sharpe") or 0.8), 4.0)
    dd = abs(d5.get("max_drawdown") or -10) / 100
    return conf * wr * (1 + sharpe / 6) * (1 - dd * 0.20)


def _choose_candidates(signals: list[dict], held: set[str]) -> list[dict]:
    sig_map = _signal_map(signals)
    cands: list[dict] = []
    for ticker, sides in sig_map.items():
        if ticker in held:
            continue
        bulls = sides["bullish"]
        if not bulls:
            continue
        top_bull = max(bulls, key=lambda s: s.get("confidence", 0))
        conf = float(top_bull.get("confidence") or 0)
        if conf < 58:
            continue
        bear_penalty = sum(_score(s) for s in sides["bearish"]) * 0.6
        net = _score(top_bull) - bear_penalty
        cands.append(
            {
                "ticker": ticker,
                "signal": top_bull.get("strategy", "Signal"),
                "confidence": conf,
                "is_crypto": ticker.endswith("-USD"),
                "score": net,
            }
        )
    cands.sort(key=lambda c: c["score"], reverse=True)
    return cands


def _open_position(state: dict, ticker: str, px: float, allocation: float, kind: str, signal: str, confidence: float) -> bool:
    if allocation <= 0 or px <= 0:
        return False
    if kind == "crypto_option":
        fee_rate = OPTION_TRADE_FEE_RATE
        slippage_rate = OPTION_SLIPPAGE_RATE
    else:
        fee_rate = SPOT_TRADE_FEE_RATE
        slippage_rate = SPOT_SLIPPAGE_RATE

    entry_fee = allocation * (fee_rate + slippage_rate)
    total_cost = allocation + entry_fee
    if total_cost > state["cash"]:
        return False

    pos = {
        "ticker": ticker,
        "type": kind,
        "allocation": round(allocation, 2),
        "entry_price": round(px, 6),
        "signal": signal,
        "confidence": confidence,
        "opened": date.today().isoformat(),
    }
    if kind == "crypto_option":
        pos["underlying"] = ticker
        pos["leverage"] = 3.0
        pos["units"] = round(allocation / px, 8)
    else:
        pos["shares"] = round(allocation / px, 8)

    state["positions"][ticker] = pos
    state["cash"] = round(state["cash"] - total_cost, 2)
    state["fees_paid"] = round(state["fees_paid"] + entry_fee, 2)
    _append_trade(
        state,
        {
            "action": "BUY_OPTION" if kind == "crypto_option" else "BUY",
            "ticker": ticker,
            "allocation": round(allocation, 2),
            "entry_price": round(px, 4),
            "fee": round(entry_fee, 2),
            "cash_after": state["cash"],
            "reason": f"{signal} ({confidence:.1f})",
        },
    )
    return True


def _close_position(state: dict, ticker: str, px: float, reason: str) -> None:
    pos = state["positions"].get(ticker)
    if not pos:
        return
    alloc = float(pos["allocation"])
    entry = float(pos["entry_price"])
    if pos["type"] == "crypto_option":
        lev = float(pos.get("leverage", 3.0))
        gross_pnl = alloc * lev * ((px - entry) / entry)
        current_value = max(0.0, alloc + gross_pnl)
        fee = current_value * (OPTION_TRADE_FEE_RATE + OPTION_SLIPPAGE_RATE)
    else:
        shares = float(pos.get("shares") or 0.0)
        current_value = shares * px
        fee = current_value * (SPOT_TRADE_FEE_RATE + SPOT_SLIPPAGE_RATE)
        gross_pnl = current_value - alloc

    net = max(0.0, current_value - fee)
    state["cash"] = round(state["cash"] + net, 2)
    state["fees_paid"] = round(state["fees_paid"] + fee, 2)
    del state["positions"][ticker]
    _append_trade(
        state,
        {
            "action": "SELL_OPTION" if pos["type"] == "crypto_option" else "SELL",
            "ticker": ticker,
            "exit_price": round(px, 4),
            "gross_pnl": round(gross_pnl, 2),
            "net_proceeds": round(net, 2),
            "fee": round(fee, 2),
            "cash_after": state["cash"],
            "reason": reason,
        },
    )


def get_max_positions(state: dict) -> int:
    cfg = state.get("config", {})
    if not isinstance(cfg, dict):
        return MAX_POSITIONS
    raw = cfg.get("max_positions", MAX_POSITIONS)
    try:
        v = int(raw)
    except (TypeError, ValueError):
        return MAX_POSITIONS
    return max(1, min(25, v))


def rebalance_aggressive(state: dict, prices: dict[str, float], signals: list[dict]) -> dict:
    sig_map = _signal_map(signals)
    held = set(state["positions"].keys())

    # Exit rules: cut losers fast, take gains faster for options, or leave when bearish dominates.
    for t in list(held):
        pos = state["positions"].get(t)
        if not pos:
            continue
        px = prices.get(t)
        if px is None:
            continue
        entry = float(pos["entry_price"])
        move_pct = (px - entry) / entry * 100

        bulls = sig_map.get(t, {}).get("bullish", [])
        bears = sig_map.get(t, {}).get("bearish", [])
        bull_score = sum(_score(s) for s in bulls)
        bear_score = sum(_score(s) for s in bears)

        if pos["type"] == "crypto_option":
            if move_pct <= -12:
                _close_position(state, t, px, "Option stop: underlying down >= 12%")
                continue
            if move_pct >= 18:
                _close_position(state, t, px, "Option take-profit: underlying up >= 18%")
                continue
        else:
            if move_pct <= -8:
                _close_position(state, t, px, "Stop-loss: down >= 8%")
                continue
            if move_pct >= 14:
                _close_position(state, t, px, "Take-profit: up >= 14%")
                continue

        if bear_score > bull_score * 1.35 and bears:
            _close_position(state, t, px, "Signal regime turned bearish")

    # Entries: aggressively deploy most free cash into strongest setups.
    held = set(state["positions"].keys())
    slots_left = max(0, get_max_positions(state) - len(held))
    if slots_left <= 0 or state["cash"] < MIN_TRADE_SIZE:
        return state

    candidates = _choose_candidates(signals, held)
    if not candidates:
        return state

    # Prefer crypto option exposure if strong crypto signal exists.
    crypto_pick = next((c for c in candidates if c["is_crypto"]), None)
    picks: list[dict] = []
    if crypto_pick:
        picks.append(crypto_pick)
    for c in candidates:
        if c in picks:
            continue
        picks.append(c)
        if len(picks) >= slots_left:
            break

    for idx, c in enumerate(picks[:slots_left]):
        ticker = c["ticker"]
        px = prices.get(ticker)
        if px is None:
            continue
        free_cash = float(state["cash"])
        if free_cash < MIN_TRADE_SIZE:
            break
        max_alloc = TOTAL_CAPITAL * MAX_SINGLE_ALLOC_PCT
        if c["is_crypto"] and idx == 0:
            target = min(max_alloc, free_cash * 0.55)
            kind = "crypto_option"
        else:
            target = min(max_alloc, free_cash * 0.45)
            kind = "spot"
        allocation = round(max(MIN_TRADE_SIZE, target), 2)
        allocation = min(allocation, free_cash * 0.95)
        if allocation < MIN_TRADE_SIZE:
            continue
        _open_position(
            state,
            ticker=ticker,
            px=px,
            allocation=allocation,
            kind=kind,
            signal=str(c.get("signal") or "Signal"),
            confidence=float(c.get("confidence") or 0.0),
        )
    return state


def mark_to_market(state: dict, prices: dict[str, float]) -> tuple[list[dict], float]:
    rows: list[dict] = []
    total_value = float(state["cash"])
    for t, pos in state["positions"].items():
        px = prices.get(t)
        if px is None:
            value = pos["allocation"]
            pnl = 0.0
        elif pos["type"] == "crypto_option":
            alloc = float(pos["allocation"])
            entry = float(pos["entry_price"])
            lev = float(pos.get("leverage", 3.0))
            gross_pnl = alloc * lev * ((px - entry) / entry)
            value = max(0.0, alloc + gross_pnl)
            pnl = value - alloc
        else:
            shares = float(pos.get("shares") or 0.0)
            value = shares * px
            pnl = value - float(pos["allocation"])

        total_value += value
        rows.append(
            {
                "ticker": t,
                "type": pos["type"],
                "allocation": float(pos["allocation"]),
                "entry_price": float(pos["entry_price"]),
                "current_price": float(px) if px else None,
                "value": round(value, 2),
                "pnl": round(pnl, 2),
                "pnl_pct": round((pnl / pos["allocation"]) * 100, 2) if pos["allocation"] else 0.0,
            }
        )
    return rows, round(total_value, 2)


def compute_benchmark(state: dict, total_value: float) -> dict:
    bm = state.get("benchmark", {})
    ticker = bm.get("ticker", "BTC-USD")
    entry = bm.get("entry_price")
    current = get_price(ticker)
    if not entry or not current:
        return {"ticker": ticker, "entry_price": entry, "current_price": current, "pnl_pct": 0.0}
    pnl_pct = (current - entry) / entry * 100
    return {
        "ticker": ticker,
        "entry_price": round(entry, 2),
        "current_price": round(current, 2),
        "pnl_pct": round(pnl_pct, 2),
        "equity_if_all_in": round(TOTAL_CAPITAL * (1 + pnl_pct / 100), 2),
        "portfolio_value": round(total_value, 2),
    }


def save_snapshot(state: dict, total_value: float, bm: dict) -> None:
    init_val = float(state["total_capital"])
    snap = {
        "date": date.today().isoformat(),
        "total_value": round(total_value, 2),
        "portfolio_pnl_pct": round((total_value - init_val) / init_val * 100, 3),
        "benchmark_pnl_pct": float(bm.get("pnl_pct") or 0.0),
        "fees_paid": round(float(state.get("fees_paid", 0.0)), 2),
    }
    snaps = [s for s in state.get("snapshots", []) if s.get("date") != snap["date"]]
    snaps.append(snap)
    state["snapshots"] = snaps


def print_report(state: dict, rows: list[dict], total_value: float, bm: dict) -> None:
    init = float(state["total_capital"])
    pnl = total_value - init
    pct = pnl / init * 100
    alpha = pct - float(bm.get("pnl_pct") or 0.0)
    fees = float(state.get("fees_paid", 0.0))
    days = (date.today() - date.fromisoformat(state["init_date"])).days

    print("\n" + "=" * 76)
    print(f"  AGGRESSIVE SIMULATION — $5K High-Risk Sleeve (Day {days})")
    print("=" * 76)
    print(f"  Cash: ${state['cash']:,.2f} | Fees paid: ${fees:,.2f}")
    print("-" * 76)
    print(f"  {'TICKER':<14} {'TYPE':<14} {'ALLOC':>9} {'VALUE':>10} {'P&L $':>10} {'P&L %':>8}")
    print("-" * 76)
    for r in rows:
        print(
            f"  {r['ticker']:<14} {r['type']:<14} "
            f"${r['allocation']:>8,.0f} ${r['value']:>9,.0f} "
            f"${r['pnl']:>+9,.0f} {r['pnl_pct']:>+7.2f}%"
        )
    if not rows:
        print("  (No open positions)")
    print("-" * 76)
    print(f"  TOTAL EQUITY: ${total_value:,.2f}  ({pct:+.2f}%, ${pnl:+,.2f})")
    print(
        f"  BENCH ({bm.get('ticker')}): {float(bm.get('pnl_pct') or 0.0):+.2f}%"
        f" | Alpha: {alpha:+.2f}%"
    )
    print("=" * 76)
    if state.get("trade_log"):
        print("  Recent trades:")
        for move in state["trade_log"][-6:]:
            stamp = move.get("timestamp", "")[:19].replace("T", " ")
            print(
                f"    [{stamp}] {move.get('action')} {move.get('ticker')} "
                f"(fee ${float(move.get('fee') or 0.0):.2f}) — {move.get('reason', '')}"
            )
        print("=" * 76)
    print()


def main() -> None:
    args = sys.argv[1:]
    if "--init" in args:
        init_simulation()
        print("Aggressive simulation initialized. State file: sim_portfolio_aggressive.json")
        return

    state = load_state()
    if not state:
        print("No aggressive simulation state found. Run: python aggressive_sim.py --init")
        return

    # Build price list from positions first, then include candidates from signals for potential entries.
    current_tickers = list(state.get("positions", {}).keys())
    prices = get_current_prices(current_tickers + ["BTC-USD", "ETH-USD", "SOL-USD"])

    try:
        from strategy_engine import run_full_scan

        signals = run_full_scan()
    except Exception as exc:
        print(f"Warning: strategy scan failed, running mark-to-market only ({exc})")
        signals = []

    for s in signals:
        t = str(s.get("ticker", "")).strip()
        if t and t not in prices:
            p = get_price(t)
            if p:
                prices[t] = p

    state = rebalance_aggressive(state, prices, signals)
    rows, total_value = mark_to_market(state, prices)
    bm = compute_benchmark(state, total_value)

    if "--snapshot" in args:
        save_snapshot(state, total_value, bm)

    save_state(state)
    print_report(state, rows, total_value, bm)


if __name__ == "__main__":
    main()
