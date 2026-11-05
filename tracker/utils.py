import re

# よく使う銘柄のローカル辞書（yfinance不要・確実）
# 必要に応じて追加してください
KNOWN_TICKERS = {
    # 米国株
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "GOOGL": "Alphabet Inc.",
    "GOOG": "Alphabet Inc.",
    "AMZN": "Amazon.com, Inc.",
    "NVDA": "NVIDIA Corporation",
    "META": "Meta Platforms, Inc.",
    "TSLA": "Tesla, Inc.",
    "NFLX": "Netflix, Inc.",
    "AMD": "Advanced Micro Devices, Inc.",
    # 日本株（コードはそのままキーに）
    "7203": "Toyota Motor Corporation",
    "6920": "Lasertec Corporation",
    "2222": "Kotobuki Spirits Co., Ltd.",
    "6758": "Sony Group Corporation",
    "9984": "SoftBank Group Corp.",
    "8306": "Mitsubishi UFJ Financial Group, Inc.",
    "9983": "Fast Retailing Co., Ltd.",
}


def detect_market(code: str):
    """銘柄コードから市場と通貨を判定（大文字基準）。
    - 数字4桁（例: 7203）                → 日本株 (JPY)
    - 数字3桁+アルファベット1文字（例: 130A） → 日本株 (JPY)
    - それ以外（例: MSFT）                → 米国株 (USD)
    """
    code = code.strip().upper()
    if re.fullmatch(r"\d{4}", code) or re.fullmatch(r"\d{3}[A-Z]", code):
        return "日本株", "JPY"
    return "米国株", "USD"


def get_company_name(code: str, market: str) -> str:
    """会社名を取得。
    ① ローカル辞書（確実・即時）
    ② yfinance（ベストエフォート・失敗してもクラッシュしない）
    どちらも失敗したら空文字（手入力で対応可）。
    """
    code = code.strip().upper()

    # ① ローカル辞書を最優先
    if code in KNOWN_TICKERS:
        return KNOWN_TICKERS[code]

    # ② yfinance を試す（失敗は握りつぶす）
    try:
        import yfinance as yf
        symbol = f"{code}.T" if market == "日本株" else code
        info = yf.Ticker(symbol).info
        name = info.get("longName") or info.get("shortName")
        if name:
            return name
    except Exception:
        pass

    # ③ 取得できなければ空（フォームの銘柄名に手入力すればOK）
    return ""