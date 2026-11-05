import os

css = r''':root{
  --bg:#181825; --bg-elev:#1e1e2e; --card:#242438; --card-2:#2a2a40;
  --line:#393956; --line-soft:#2f2f47;
  --text:#cdd6f4; --text-dim:#a6adc8; --muted:#7f849c;
  --green:#a6e3a1; --red:#f38ba8; --yellow:#f9e2af; --blue:#89b4fa;
  --sapphire:#74c7ec; --mauve:#cba6f7; --peach:#fab387;
  --radius:14px; --radius-sm:9px;
  --shadow:0 10px 30px rgba(0,0,0,0.35); --shadow-sm:0 4px 14px rgba(0,0,0,0.25);
  --ring:0 0 0 3px rgba(137,180,250,0.28);
  --font:"Meiryo UI","Meiryo","Segoe UI",system-ui,sans-serif; --maxw:1180px;
}
*{box-sizing:border-box;}
body{margin:0;background:var(--bg);color:var(--text);font-family:var(--font);line-height:1.6;}
a{color:var(--blue);text-decoration:none;}
a:hover{text-decoration:underline;}
.nav{position:sticky;top:0;z-index:50;display:flex;align-items:center;gap:8px;padding:14px 24px;background:rgba(24,24,37,0.85);backdrop-filter:blur(12px);border-bottom:1px solid var(--line-soft);}
.nav .brand{font-size:1.2rem;font-weight:800;display:flex;align-items:center;gap:8px;margin-right:16px;}
.nav .brand .logo{font-size:1.35rem;}
.nav .links{display:flex;gap:4px;}
.nav .links a{color:var(--text-dim);padding:8px 14px;border-radius:10px;font-size:.95rem;font-weight:600;}
.nav .links a:hover{background:var(--card);color:var(--text);}
.nav .links a.active{background:var(--blue);color:#11111b;}
.nav .spacer{flex:1;}
.nav .user{color:var(--muted);font-size:.9rem;margin-right:6px;}
.container{max-width:var(--maxw);margin:0 auto;padding:28px 24px 64px;}
.page-head{display:flex;align-items:center;gap:14px;margin-bottom:22px;flex-wrap:wrap;}
.page-head h1{font-size:1.7rem;margin:0;font-weight:800;}
.page-head .spacer{flex:1;}
.btn{display:inline-flex;align-items:center;gap:8px;background:var(--card);color:var(--text);border:1px solid var(--line);border-radius:11px;padding:10px 18px;font-size:.95rem;font-weight:600;font-family:inherit;cursor:pointer;transition:all .15s;text-decoration:none;}
.btn:hover{border-color:var(--blue);transform:translateY(-1px);text-decoration:none;}
.btn--primary{background:linear-gradient(135deg,var(--blue),var(--sapphire));color:#0b1020;border:none;box-shadow:var(--shadow-sm);}
.btn--ghost{background:transparent;}
.btn--danger{background:transparent;color:var(--red);border-color:rgba(243,139,168,.5);}
.btn--danger:hover{background:var(--red);color:#11111b;}
.btn--sm{padding:6px 12px;font-size:.85rem;border-radius:9px;}
.btn--lg{padding:13px 34px;font-size:1.1rem;}
.card{background:linear-gradient(180deg,var(--card),var(--bg-elev));border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);padding:24px;}
.toasts{position:fixed;top:74px;right:20px;z-index:100;display:flex;flex-direction:column;gap:10px;}
.toast{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--green);border-radius:10px;padding:12px 18px;box-shadow:var(--shadow);font-size:.92rem;min-width:220px;}
.toast.error{border-left-color:var(--red);}
.input{width:100%;font-size:1.05rem;font-family:inherit;padding:11px 14px;color:var(--text);background:var(--bg-elev);border:1px solid var(--line);border-radius:var(--radius-sm);}
.input:focus{outline:none;border-color:var(--blue);box-shadow:var(--ring);}
.input--num{text-align:right;font-variant-numeric:tabular-nums;}
.input--ticker{text-transform:uppercase;letter-spacing:.04em;font-weight:700;}
textarea.input{resize:vertical;min-height:60px;}
::placeholder{color:#5c5f7a;}
.field{display:flex;flex-direction:column;}
.field > label{font-size:1rem;font-weight:700;margin-bottom:6px;color:var(--text);}
.field .hint{font-size:.8rem;color:var(--muted);margin-top:4px;}
.field .status{font-size:.82rem;margin-top:4px;min-height:1em;}
.field .status.ok{color:var(--green);}
.field .status.loading{color:var(--yellow);}
.errorlist{color:var(--red);list-style:none;padding:0;margin:6px 0 0;font-size:.85rem;}
.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px 26px;}
.form-grid .full{grid-column:1 / -1;}
.form-actions{display:flex;align-items:center;gap:14px;justify-content:center;margin-top:26px;flex-wrap:wrap;}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:22px;}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:18px 20px;}
.kpi .label{color:var(--muted);font-size:.85rem;display:flex;align-items:center;gap:6px;}
.kpi .value{font-size:1.7rem;font-weight:800;margin-top:6px;font-variant-numeric:tabular-nums;}
.cards-2{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:24px;}
.ccard{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:22px;}
.ccard h2{font-size:1.15rem;margin:0 0 16px;text-align:center;}
.crow{display:flex;justify-content:space-between;align-items:center;padding:9px 4px;border-bottom:1px solid var(--line-soft);}
.crow:last-of-type{border-bottom:none;}
.crow .k{color:var(--muted);font-size:.9rem;}
.crow .v{font-weight:700;font-size:1.05rem;font-variant-numeric:tabular-nums;}
.pf-eval{text-align:center;margin-top:14px;padding:8px;border-radius:9px;background:var(--bg-elev);color:var(--yellow);font-size:.92rem;font-weight:600;}
.charts{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:24px;}
.chartbox{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:18px;}
.chartbox h3{font-size:1rem;margin:0 0 12px;text-align:center;}
.table-wrap{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow-sm);}
table{width:100%;border-collapse:collapse;}
th,td{padding:12px 14px;font-size:.9rem;text-align:left;border-bottom:1px solid var(--line-soft);}
th{background:var(--card-2);color:var(--text-dim);font-weight:700;font-size:.82rem;letter-spacing:.03em;}
tbody tr:hover{background:var(--card-2);}
td.num{text-align:right;font-variant-numeric:tabular-nums;}
.badge{display:inline-block;padding:3px 10px;border-radius:999px;font-size:.8rem;font-weight:700;}
.badge.buy{background:rgba(166,227,161,.15);color:var(--green);}
.badge.sell{background:rgba(243,139,168,.15);color:var(--red);}
.badge.jp{background:rgba(137,180,250,.15);color:var(--blue);}
.badge.us{background:rgba(250,179,135,.15);color:var(--peach);}
.profit{color:var(--green);font-weight:700;}
.loss{color:var(--red);font-weight:700;}
.toolbar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:18px;}
.toolbar .input{width:auto;min-width:200px;}
.toolbar select.input{min-width:130px;}
.pagination{display:flex;gap:6px;justify-content:center;margin-top:22px;align-items:center;}
.pagination a,.pagination span{padding:7px 13px;border-radius:9px;border:1px solid var(--line);color:var(--text-dim);font-size:.9rem;}
.pagination .current{background:var(--blue);color:#11111b;border-color:var(--blue);font-weight:700;}
.empty{text-align:center;color:var(--muted);padding:60px 20px;}
.empty .icon{font-size:2.6rem;margin-bottom:10px;}
.auth-wrap{max-width:400px;margin:8vh auto;}
.auth-wrap h1{text-align:center;font-size:1.6rem;margin:0 0 6px;}
.auth-wrap .sub{text-align:center;color:var(--muted);margin-bottom:24px;}
@media(max-width:860px){.kpis{grid-template-columns:repeat(2,1fr);}.cards-2,.charts{grid-template-columns:1fr;}}
@media(max-width:620px){.form-grid{grid-template-columns:1fr;}.nav{padding:12px 14px;}.container{padding:20px 14px 48px;}th,td{padding:9px 8px;}}
'''

os.makedirs("tracker/static/tracker/css", exist_ok=True)
with open("tracker/static/tracker/css/app.css", "w", encoding="utf-8") as f:
    f.write(css)
print("app.css を作成しました:", len(css), "bytes")