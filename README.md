# 📈 Trade Journal — 株式トレードジャーナル (Django版 / JP・US)

日本株・米国株の売買履歴を記録し、**勝率・プロフィットファクター（PF）・銘柄別損益**を可視化する **Django Web アプリ** です。
Tkinter デスクトップ版から移植し、**マルチユーザー対応・認証付き** の Web アプリケーションとして再構築しました。

---

## 🏗️ 技術スタック

| 分類 | 使用技術 |
|---|---|
| フレームワーク | Django **6.0.6** |
| 言語 | Python 3.13 |
| DB | SQLite3（開発）／PostgreSQL（本番想定） |
| 分析 | pandas / numpy |
| グラフ | Chart.js 4.4.1（CDN） |
| 銘柄名取得 | yfinance（ベストエフォート） |
| 認証 | Django 標準認証（django.contrib.auth） |
| フォント | Meiryo UI（ダークテーマ） |

---

## 🗂️ プロジェクト構成

```
Trade_Journal/
├── manage.py
├── db.sqlite3
├── requirements.txt
├── trades.csv                 # 初期データ（任意）
├── tradejournal/              # プロジェクト設定
│   ├── settings.py            # INSTALLED_APPS, LOGIN系, ja/Asia-Tokyo
│   └── urls.py                # accounts/ + tracker をinclude
└── tracker/                   # アプリ本体
    ├── models.py              # Trade モデル
    ├── forms.py               # TradeForm（入力改善版）
    ├── views.py               # 一覧/登録/削除/分析/lookup API
    ├── utils.py               # detect_market / get_company_name
    ├── analytics.py           # calculate_stats（pandas・matplotlib非依存）
    ├── urls.py                # アプリ内ルーティング
    ├── migrations/
    ├── management/commands/
    │   └── import_trades.py    # CSV取り込みコマンド
    └── templates/
        ├── registration/
        │   └── login.html      # ログイン画面
        └── tracker/
            ├── base.html       # 共通レイアウト（ナビ/ログアウト）
            ├── trade_list.html # トレード一覧
            ├── trade_form.html # 登録フォーム（AJAX自動入力）
            └── analysis.html   # パフォーマンス分析（Chart.js）
```

### モジュール責務
- **models.py** — `Trade` モデル。`user` ForeignKey でユーザー別にデータ分離。`as_stats_row()` で分析用の日本語キー辞書に変換
- **utils.py** — `detect_market()`（市場・通貨判定）、`get_company_name()`（yfinance会社名取得）
- **analytics.py** — `calculate_stats()`。Tkinter版から流用。matplotlib/tkinter依存を除去し、`pf=∞` を `None` に変更（JSON対応）
- **views.py** — `trade_list` / `trade_create` / `trade_delete` / `analysis` / `lookup_company`(API)
- **テンプレート** — グラフは Chart.js がブラウザ側で描画（Python側に描画コードなし）

---

## ✨ 主な機能

| 機能 | 説明 |
|---|---|
| 📝 トレード記録 | 日時・銘柄・売買・数量・価格・手数料・備考を保存 |
| 🔐 マルチユーザー | ログイン必須。各ユーザーは自分のトレードのみ閲覧（`filter(user=request.user)`） |
| 🔍 市場自動判定 | 銘柄コードから市場・通貨を自動分類（下記ルール） |
| 🔡 大文字正規化 | Ticker入力を自動で大文字化（例: `msft` → `MSFT`） |
| 🏢 銘柄名自動取得 | yfinance で会社名を取得（日本株は `.T` 付与）。フォームで欄を離れると自動入力（AJAX） |
| 🕒 日時入力 | `datetime-local` で年月日＋時:分を選択。デフォルトで現在時刻をセット |
| 📊 パフォーマンス分析 | 総トレード数 / 勝率 / PF / 総損益 / 平均損益 を **通貨別（JPY/USD）** に集計 |
| 📈 可視化 | Chart.js で「銘柄別損益（棒）」「勝率（ドーナツ）」を JPY/USD ごとに表示 |
| 💾 CSV取り込み | `import_trades` 管理コマンドで `trades.csv` を一括投入 |

### 市場自動判定ルール（detect_market）

| 銘柄コード | 判定 | 例 |git 
|---|---|---|
| 数字4桁 | 日本株 (JPY) | `7203` |
| 数字3桁＋アルファベット1文字 | 日本株 (JPY) | `130A`（新形式） |
| それ以外（アルファベット） | 米国株 (USD) | `AAPL` |

---

## 🚀 セットアップ

### 1. 仮想環境と依存インストール
```powershell
cd Trade_Journal
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install django pandas numpy yfinance
```

### 2. マイグレーション
```powershell
python manage.py migrate
```

### 3. 管理ユーザー作成
```powershell
python manage.py createsuperuser
```

### 4. 初期データ取り込み（任意）
```powershell
python manage.py import_trades trades.csv --user <ユーザー名>
```
- エンコーディング: `utf-8-sig`（BOM付きUTF-8）対応
- 日付形式: `YYYY-MM-DD` / `YYYY/MM/DD` 両対応

### 5. 起動
```powershell
python manage.py runserver
```
→ `http://127.0.0.1:8000/`（未ログイン時はログイン画面へリダイレクト）

---

## 🔗 URL 一覧

| URL | 機能 | name |
|---|---|---|
| `/` | トレード一覧 | `trade_list` |
| `/add/` | 新規登録 | `trade_create` |
| `/<id>/delete/` | 削除 | `trade_delete` |
| `/analysis/` | パフォーマンス分析 | `analysis` |
| `/api/lookup/` | 銘柄名取得API（AJAX） | `lookup_company` |
| `/accounts/login/` | ログイン | `login` |
| `/accounts/logout/` | ログアウト | `logout` |
| `/admin/` | 管理画面 | — |

---

## 📊 分析ロジック（calculate_stats）

銘柄ごとに以下を計算（**買い・売りの両方がある銘柄のみ** 損益確定）:

- **買いコスト** = Σ(数量 × 価格 + 手数料)
- **売り収益** = Σ(数量 × 価格 − 手数料)
- **損益** = 売り収益 − 買いコスト

通貨別（JPY / USD）に集計:

| 指標 | 計算式 |
|---|---|
| 勝率 | 利益銘柄数 ÷ 全銘柄数 × 100 |
| PF | Σ利益 ÷ Σ損失（損失0なら `None`＝∞表示） |
| 総損益 | Σ損益 |
| 平均損益 | mean(損益) |

**PF評価**: ≥2.0 優秀 ✅／≥1.5 良好 👍／≥1.0 分岐点以上 ⚠️／<1.0 改善が必要 ❌

---

## 🐛 移植時の主なトラブルと解決（記録）

| 症状 | 原因 | 解決 |
|---|---|---|
| `django-admin` not found | venvにDjango未インストール | `python -m django startproject … .`（末尾ドット） |
| `ImportError: relative import beyond top-level` | views.pyの `from ..analytics`（移動前の名残） | `..` → `.` に修正 |
| models.py 日本語が文字化け（`譌･譛ｬ譬ｪ`） | Shift-JIS保存 | UTF-8で全置換保存 |
| `No changes detected` | migrationは既に適用済み | 正常（誤認だった） |
| `User.DoesNotExist` | 取込時のユーザー未作成 | `createsuperuser` 先行 |
| 企業名が表示されない | 入力中ではなく**保存後**に取得する仕様 | 仕様。保存後の一覧で表示 |
| `Unexpected token '.'` | テンプレJSの行欠落・script内にstyle混入 | analysis.html 全置換 |
| グラフが出ない | Chart.jsが `<a>`リンク化 | `<script src=…>` に修正 |
| 値が全て `undefined`（`typeof s === "string"`） | `json.dumps` ＋ `json_script` の**二重エンコード** | views.pyの `json.dumps` を外し `stats or {}` を渡す |

> ⚠️ **コード破損の再発防止**: コードはチャット欄を経由せず、エディタに直接貼ること（URL自動リンク化・行欠落の事故防止）。

---

## ⚠️ 既知の課題・注意点

- **yfinance の不安定さ**: Yahoo Finance 非公式APIのため、レート制限（429）や仕様変更で会社名取得が失敗することがある。本番ではローカル辞書方式 or 公式API（Alpha Vantage等）への移行を推奨。銘柄名は手入力でも運用可能
- **テストデータの混入**: 動作確認で追加した取引（例: Toyota 7203 の重複買い）が損益を歪めることがある。発表前にクリーンアップが必要
- **SQLite の本番非推奨**: Azure App Service 等の揮発ストレージではデータ消失リスク。本番は **PostgreSQL** へ移行
- **開発サーバー**: `runserver` は本番不可。本番は WSGI/ASGI サーバーを使用

---

## 🛣️ 今後の拡張アイデア

- [ ] PostgreSQL 移行（本番DB）
- [ ] Azure App Service デプロイ（whitenoise / 静的ファイル配信）
- [ ] yfinance の非同期化 or 公式APIへの置き換え
- [ ] Chart.js のローカル配置（CDN遮断環境対応）
- [ ] CSV / Excel エクスポート
- [ ] 為替レート連動の JPY/USD 統合 P&L
- [ ] 月次・年次の時系列損益グラフ（drawdown 曲線）

---

## 📄 License
MIT（任意で変更してください）
