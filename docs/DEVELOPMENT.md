# 開発メモ

README から移した、開発者向けの記録です。アプリの概要・セットアップ・使い方は [README](../README.md) を参照してください。

## 目次

- [開発の経緯](#開発の経緯)
- [モジュールの役割](#モジュールの役割)
- [開発用のコマンド](#開発用のコマンド)
- [移植時の主なトラブルと解決](#移植時の主なトラブルと解決)
- [コード破損の再発防止](#コード破損の再発防止)
- [既知の不具合と改善候補](#既知の不具合と改善候補)
- [使われていないファイル](#使われていないファイル)

## 開発の経緯

1. **Tkinter 版**：最初は Tkinter（Python 標準の GUI ライブラリ）で作ったデスクトップアプリでした。ソースコードはこのリポジトリには含まれていません。`requirements.txt`（tkcalendar、matplotlib など）はこの版のものです。
2. **Django への移植**：ログイン必須で、ユーザーごとにデータを分ける Web アプリとして作り直しました。分析ロジック（`calculate_stats()`）は Tkinter 版から流用し、matplotlib・tkinter への依存を取り除いて、PF の ∞ を JSON で扱えるように `None` で表すように変えました。
3. **全面的な作り直し**：損益の計算を移動平均法に改め、保有中の建玉を表示するようにしました。あわせて、画面デザインと分析ダッシュボードの刷新、編集・検索・CSV 出力の追加、`services.py` への処理の集約、Chart.js の同梱、テスト（11 件）の追加を行いました。

## モジュールの役割

- **`tracker/models.py`**：`Trade` モデル。`user` の外部キーでユーザーごとにデータを分けます。市場・売買・通貨は `TextChoices` です。
- **`tracker/services.py`**：銘柄コードの正規化（`normalize_ticker()`）、市場・通貨の判定（`detect_market()`）、銘柄名の取得（`get_company_name()`。辞書 → キャッシュ → yfinance）、保存前に市場・通貨・銘柄名をそろえる処理（`resolve_trade_fields()`）。
- **`tracker/analytics.py`**：`calculate_stats()`。移動平均法で銘柄ごとの損益を計算し、通貨別の指標・銘柄別の損益・保有中の建玉を辞書で返します。
- **`tracker/views.py`**：`trade_list` / `trade_create` / `trade_edit` / `trade_delete` / `analysis` / `lookup_company`（API）/ `export_csv`。
- **`tracker/forms.py`**：`TradeForm`。約定日時は `datetime-local` で初期値は現在時刻、手数料の空欄は 0 として扱います。
- **`tracker/management/commands/import_trades.py`**：CSV 取り込みコマンド。1 つのトランザクションで登録します。
- **テンプレート**：グラフは Chart.js がブラウザ側で描きます（Python 側に描画コードはありません）。集計結果は `json_script` で受け取ります。

## 開発用のコマンド

```bash
python manage.py check                              # 設定とモデルの検査
python manage.py makemigrations --check --dry-run   # マイグレーションの作り忘れの確認
python manage.py test                               # テスト（11 件）
python manage.py check --deploy                     # 本番向け設定の確認（今の設定では警告 7 件）
```

## 移植時の主なトラブルと解決

Tkinter 版から Django に移植したときの記録です。当時の状況なので、今のコードとは異なるものもあります。

| 症状                                              | 原因                                                        | 解決                                                    |
| ------------------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------- |
| `django-admin` が見つからない                     | 仮想環境に Django が入っていなかった                        | Django を入れ、`python -m django` で実行した            |
| `ImportError`（relative import beyond top-level） | `views.py` に残っていた `from ..analytics`                  | `..` を `.` に直した                                    |
| `models.py` の日本語が文字化けする（`譌･譛ｬ譬ｪ`） | ファイルが Shift_JIS で保存されていた                       | UTF-8 で保存し直した                                    |
| `No changes detected`                             | モデルに変更がなく、マイグレーションは作成済みだった        | エラーではなく、正常な表示だった                        |
| `User.DoesNotExist`                               | CSV を取り込む前に、ユーザーを作っていなかった              | 先に `createsuperuser` でユーザーを作った               |
| 会社名が表示されない                              | 当時は、保存したときに取得する仕様だった                    | 仕様どおり（今は銘柄コードの欄を離れると自動入力する）  |
| `Unexpected token '.'`（JavaScript）              | JavaScript の行の欠落と、`<script>` 内への `<style>` の混入 | `analysis.html` を全体的に置き換えた                    |
| グラフが表示されない                              | Chart.js の `<script>` タグが `<a>` タグに変わっていた      | `<script src="...">` に戻した                           |
| 値がすべて `undefined` になる                     | `json.dumps` と `json_script` による二重エンコード          | `views.py` で `json.dumps` をやめ、辞書をそのまま渡した |

## コード破損の再発防止

コードをコピーして反映するときは、チャットツールなどを経由せず、エディタに直接貼り付けてください。URL の自動リンク化や行の欠落で、コードが壊れることがあります。

今のテンプレートにも、`<a href="...">` の開始タグが欠けた箇所が 2 つ残っています（次の節を参照）。

## 既知の不具合と改善候補

README の「既知の制限」に加えて、コードを読んで見つけた点です。いずれも未修正です。

- **依存関係の定義**：`requirements.txt` は Tkinter 版のもので、Django が含まれていません。Web 版の依存関係（`Django>=6.0,<6.1`、`yfinance`）に置き換えれば、README の手順を `pip install -r requirements.txt` にできます。
- **CI の設定**：`azure-pipelines.yml` は、Python 3.8〜3.10 で `requirements.txt` を入れる設定です。Web 版は Django 6.0 を使うため Python 3.12 以上が必要で、この設定とは合っていません。
- **テンプレートの BOM**：`base.html`、`trade_list.html`、`trade_form.html`、`analysis.html` が BOM 付きの UTF-8 で保存されています。テンプレートの継承によって HTML の先頭（`<!DOCTYPE html>` の前）に BOM の文字が出力され、ブラウザが互換モード（Quirks モード）で描画するため、ナビゲーションの上に余白ができます。
- **リンクの開始タグの欠落**：`trade_form.html` の「キャンセル」と、`analysis.html` のデータがないときの「トレードを登録」で `<a href="...">` が欠けていて、「/キャンセル」のように URL と文字がそのまま表示されます。
- **編集画面**：見出しが常に「新規トレード登録」です（ビューは `mode` を渡していますが、テンプレートで使っていません）。また、`trade_create` は `save_and_add`（保存して続けて登録）に対応していますが、そのボタンがありません。
- **CSS のクラス名**：`login.html` と `trade_form.html` の `btn-primary`、`base.html` の `btn-danger` は、`app.css` の定義（`btn--primary`、`btn--danger`）と名前が合っていません（`trade_form.html` はページ内のスタイルで補っています）。メッセージ表示（`ul.messages`）のスタイルもありません。
- **CSV 出力**：`export_csv` は、`charset=utf-8-sig` の指定と `\ufeff` の書き込みが重なって、各行の先頭に BOM が付きます。日時も UTC のまま出力されます。そのため、出力したファイルを `import_trades` で読み込むと「日付を解釈できません」というエラーになります。
- **CSV 取り込み**：`Trade.objects.create()` で登録するため、モデルの選択肢や最小値の検証が行われません（例：売買が「X」、数量が -100 の行もそのまま登録されます）。重複の検出もありません。
- **集計**：保有数量を超える売りや、買いの記録がない売りは、売却代金がそのまま利益になります。損失の銘柄がないときは、利益がなくても（損益 0 の銘柄だけでも）PF が「∞」、評価が「損失なし」になります。
- **設定**：`SECRET_KEY` が `settings.py` に直接書かれて公開されています。`DEBUG = True`、`ALLOWED_HOSTS = []` のままで、`check --deploy` では 7 件の警告（W004、W008、W009、W012、W016、W018、W020）が出ます。

## 使われていないファイル

Web アプリの実行には使われていない、旧版や作業用のファイルです。整理するときの参考にしてください。

| パス                                            | 内容                                                                                                          |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `tracker/utils.py`                              | `services.py` と同じ役割の旧版（どこからも読み込まれていない）                                                |
| `tracker/fix_analysis.py`、`tracker/fix_css.py` | `analysis.html`・`app.css` を書き出す一回限りのスクリプト（中身が古く、実行すると今のファイルが上書きされる） |
| `tracker/templates/tracker/preview_form.html`   | 登録画面のデザインを確認するための静的なモック                                                                |
| `trade_journal_web.html`                        | サーバーなしで動く試作版（旧方式の集計、Chart.js は CDN から読み込む）                                        |
| `Trade_Journal.pyproj`、`Trade_Journal.slnx`    | IDE のプロジェクトファイル（`.pyproj` は存在しない `Trade_Journal.py` を参照）                                |
