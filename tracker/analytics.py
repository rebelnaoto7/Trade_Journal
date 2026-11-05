from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
from .models import Currency, Side


@dataclass
class _Symbol:
    ticker: str
    name: str
    market: str
    currency: str
    realized_pnl: float = 0.0
    realized_cost: float = 0.0
    open_qty: float = 0.0
    open_cost: float = 0.0
    closed: bool = False

    @property
    def return_pct(self) -> float:
        return (self.realized_pnl / self.realized_cost * 100) if self.realized_cost > 0 else 0.0

    @property
    def avg_open_price(self) -> float:
        return (self.open_cost / self.open_qty) if self.open_qty > 0 else 0.0


def _f(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def _compute_symbol(trades: list) -> _Symbol:
    t0 = trades[0]
    s = _Symbol(ticker=t0.ticker, name=t0.name, market=t0.market, currency=t0.currency)
    qty_held = 0.0
    cost_held = 0.0
    for t in sorted(trades, key=lambda x: (x.date or datetime.min, x.id)):
        qty, price, fee = _f(t.quantity), _f(t.price), _f(t.fee)
        if t.side == Side.BUY:
            cost_held += qty * price + fee
            qty_held += qty
        elif t.side == Side.SELL:
            s.closed = True
            if qty_held <= 0:
                s.realized_pnl += qty * price - fee
                continue
            matched = min(qty, qty_held)
            avg_cost = cost_held / qty_held
            cost_part = avg_cost * matched
            s.realized_pnl += (matched * price - fee) - cost_part
            s.realized_cost += cost_part
            qty_held -= matched
            cost_held -= cost_part
            extra = qty - matched
            if extra > 0:
                s.realized_pnl += extra * price
    s.open_qty = round(qty_held, 6)
    s.open_cost = round(cost_held, 2)
    return s


def calculate_stats(trades: Iterable) -> dict | None:
    trades = list(trades)
    if not trades:
        return None
    grouped: dict[str, list] = {}
    for t in trades:
        grouped.setdefault(t.ticker, []).append(t)
    symbols = [_compute_symbol(v) for v in grouped.values()]

    def summarize(cur: str) -> dict:
        syms = [s for s in symbols if s.currency == cur and s.closed]
        if not syms:
            return {"win_rate": 0, "pf": None, "total_pnl": 0, "avg_pnl": 0,
                    "count": 0, "win_count": 0, "loss_count": 0, "return_pct": 0}
        wins = [s for s in syms if s.realized_pnl > 0]
        losses = [s for s in syms if s.realized_pnl < 0]
        gp = sum(s.realized_pnl for s in wins)
        gl = abs(sum(s.realized_pnl for s in losses))
        total = sum(s.realized_pnl for s in syms)
        cost = sum(s.realized_cost for s in syms)
        return {
            "win_rate": round(len(wins) / len(syms) * 100, 2),
            "pf": round(gp / gl, 2) if gl > 0 else None,
            "total_pnl": round(total, 2),
            "avg_pnl": round(total / len(syms), 2),
            "count": len(syms),
            "win_count": len(wins),
            "loss_count": len(losses),
            "return_pct": round(total / cost * 100, 2) if cost > 0 else 0,
        }

    def pnl_list(cur: str) -> list[dict]:
        items = [s for s in symbols if s.currency == cur and s.closed]
        items.sort(key=lambda s: s.realized_pnl, reverse=True)
        return [{"ticker": s.ticker, "name": s.name, "pnl": round(s.realized_pnl, 2),
                 "return_pct": round(s.return_pct, 2)} for s in items]

    def open_list(cur: str) -> list[dict]:
        items = [s for s in symbols if s.currency == cur and s.open_qty > 0]
        return [{"ticker": s.ticker, "name": s.name, "qty": s.open_qty,
                 "avg_price": round(s.avg_open_price, 2), "cost": s.open_cost} for s in items]

    return {
        "total_trades": len(trades),
        "buy_count": sum(1 for t in trades if t.side == Side.BUY),
        "sell_count": sum(1 for t in trades if t.side == Side.SELL),
        "jpy": summarize(Currency.JPY),
        "usd": summarize(Currency.USD),
        "pnl_jpy": pnl_list(Currency.JPY),
        "pnl_usd": pnl_list(Currency.USD),
        "open_jpy": open_list(Currency.JPY),
        "open_usd": open_list(Currency.USD),
    }