"""Unit tests for simulation daily update (no yfinance / network)."""
import os
import sys
import types
from importlib.util import module_from_spec, spec_from_file_location

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_portfolio_sim():
    sys.modules.pop("portfolio_sim", None)
    logs_dir = os.path.join(_ROOT, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    yf = types.ModuleType("yfinance")
    yf.Ticker = lambda *a, **k: None
    sys.modules["yfinance"] = yf
    dotenv = types.ModuleType("dotenv")

    def _noop(*_a, **_k):
        return None

    dotenv.load_dotenv = _noop
    sys.modules["dotenv"] = dotenv
    path = os.path.join(_ROOT, "portfolio_sim.py")
    spec = spec_from_file_location("portfolio_sim", path)
    mod = module_from_spec(spec)
    sys.modules["portfolio_sim"] = mod
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def test_simulation_daily_update_top_bullish_and_blocks():
    p = _load_portfolio_sim()

    state = {
        "positions": {
            "CASH": {"type": "cash", "allocation": 120_000.0},
            "XLE": {"type": "market", "status": "open", "allocation": 1000},
        },
        "trade_log": [],
    }

    def sig(ticker, direction, strategy, confidence):
        return {
            "ticker": ticker,
            "direction": direction,
            "strategy": strategy,
            "confidence": confidence,
            "backtest": {"5d": {"win_rate": 60, "sharpe": 1.0, "max_drawdown": -10}},
        }

    # Top bullish by confidence: AAPL weaker bull line than strongest on ticker (tests "informational" branch)
    signals = [
        sig("AAPL", "BULLISH", "Minor Bull", 90),
        sig("AAPL", "BULLISH", "Major Bull", 95),
        sig("MSFT", "BEARISH", "Big Bear", 80),
        sig("MSFT", "BULLISH", "Setup", 70),
        sig("XLE", "BULLISH", "In port", 88),
        sig("BLOCKED", "BULLISH", "Lonely Bull", 80),
        sig("BLOCKED", "BEARISH", "Conflict", 79),
    ]

    sig_map = p.build_sig_map(signals)
    in_pf = set(state["positions"].keys())
    candidates = p.gather_ranked_new_candidates(sig_map, in_pf)
    selected = p.select_new_opportunity_candidates(candidates)
    recs = [
        {"ticker": "XLE", "action": "HOLD", "priority": "low", "reason": "ok", "tax_note": ""},
    ]
    du = p.simulation_daily_update(state, signals, recs, 120_000.0, candidates, selected)

    assert du["date"]
    assert "120,000" in du["intro"] or "120000" in du["intro"].replace(",", "")
    text = "\n".join(du["bullets"])
    assert "AAPL" in text and "strongest bullish" in text.lower()
    assert "XLE" in text and "portfolio" in text.lower()
    assert "BLOCKED" in text and "78" in text


def test_format_simulation_daily_update_html_escapes():
    p = _load_portfolio_sim()
    frag = p.format_simulation_daily_update_html(
        {"intro": "a<b>", "bullets": ["tick & run"], "summary": "ok"}
    )
    assert "&lt;" in frag or "&amp;" in frag
    assert "<b>" not in frag or "&lt;b&gt;" in frag
