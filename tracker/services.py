from __future__ import annotations
import re
from django.core.cache import cache
from .models import Currency, Market

KNOWN_TICKERS: dict[str, str] = {
    "AAPL": "Apple Inc.", "MSFT": "Microsoft Corporation", "GOOGL": "Alphabet Inc.",
    "GOOG": "Alphabet Inc.", "AMZN": "Amazon.com, Inc.", "NVDA": "NVIDIA Corporation",
    "META": "Meta Platforms, Inc.", "TSLA": "Tesla, Inc.", "NFLX": "Netflix, Inc.",
    "AMD": "Advanced Micro Devices, Inc.",
    "7203": "Toyota Motor Corporation", "6920": "Lasertec Corporation",
    "2222": "Kotobuki Spirits Co., Ltd.", "6758": "Sony Group Corporation",
    "9984": "SoftBank Group Corp.", "8306": "Mitsubishi UFJ Financial Group, Inc.",
    "9983": "Fast Retailing Co., Ltd.",
}
_JP_4DIGIT = re.compile(r"^\d{4}$")
_JP_NEW = re.compile(r"^\d{3}[A-Z]$")


def normalize_ticker(code: str) -> str:
    return (code or "").strip().upper()


def detect_market(code: str) -> tuple[str, str]:
    code = normalize_ticker(code)
    if _JP_4DIGIT.match(code) or _JP_NEW.match(code):
        return Market.JP, Currency.JPY
    return Market.US, Currency.USD


def get_company_name(code: str, market: str) -> str:
    code = normalize_ticker(code)
    if not code:
        return ""
    if code in KNOWN_TICKERS:
        return KNOWN_TICKERS[code]
    cache_key = f"company_name:{code}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    name = ""
    try:
        import yfinance as yf
        symbol = f"{code}.T" if market == Market.JP else code
        info = yf.Ticker(symbol).info
        name = info.get("longName") or info.get("shortName") or ""
    except Exception:
        name = ""
    cache.set(cache_key, name, timeout=60 * 60 * 24 if name else 60 * 5)
    return name


def resolve_trade_fields(code: str, current_name: str = "") -> dict:
    code = normalize_ticker(code)
    market, currency = detect_market(code)
    name = current_name or get_company_name(code, market)
    return {"ticker": code, "market": market, "currency": currency, "name": name}