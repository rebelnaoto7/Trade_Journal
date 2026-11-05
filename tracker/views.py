from __future__ import annotations
import csv
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .analytics import calculate_stats
from .forms import TradeForm
from .models import Trade
from .services import detect_market, get_company_name, normalize_ticker, resolve_trade_fields


@login_required
def trade_list(request):
    qs = Trade.objects.filter(user=request.user)
    q = request.GET.get("q", "").strip()
    side = request.GET.get("side", "").strip()
    if q:
        qs = (qs.filter(ticker__icontains=q) | qs.filter(name__icontains=q)).filter(user=request.user)
    if side in ("買", "売"):
        qs = qs.filter(side=side)
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "tracker/trade_list.html", {"page": page, "q": q, "side": side, "total": qs.count()})


@login_required
def trade_create(request):
    if request.method == "POST":
        form = TradeForm(request.POST)
        if form.is_valid():
            trade = form.save(commit=False)
            trade.user = request.user
            r = resolve_trade_fields(trade.ticker, trade.name)
            trade.ticker, trade.market, trade.currency, trade.name = r["ticker"], r["market"], r["currency"], r["name"]
            trade.save()
            messages.success(request, f"{trade.ticker} の{trade.side}を登録しました。")
            if "save_and_add" in request.POST:
                return redirect("trade_create")
            return redirect("trade_list")
    else:
        form = TradeForm()
    return render(request, "tracker/trade_form.html", {"form": form, "mode": "create"})


@login_required
def trade_edit(request, pk):
    trade = get_object_or_404(Trade, pk=pk, user=request.user)
    if request.method == "POST":
        form = TradeForm(request.POST, instance=trade)
        if form.is_valid():
            trade = form.save(commit=False)
            r = resolve_trade_fields(trade.ticker, trade.name)
            trade.ticker, trade.market, trade.currency, trade.name = r["ticker"], r["market"], r["currency"], r["name"]
            trade.save()
            messages.success(request, "更新しました。")
            return redirect("trade_list")
    else:
        form = TradeForm(instance=trade)
    return render(request, "tracker/trade_form.html", {"form": form, "mode": "edit", "trade": trade})


@login_required
def trade_delete(request, pk):
    trade = get_object_or_404(Trade, pk=pk, user=request.user)
    if request.method == "POST":
        trade.delete()
        messages.success(request, "削除しました。")
    return redirect("trade_list")


@login_required
def analysis(request):
    trades = list(Trade.objects.filter(user=request.user))
    stats = calculate_stats(trades)
    return render(request, "tracker/analysis.html", {"stats": stats, "stats_data": stats or {}})


@login_required
def lookup_company(request):
    code = normalize_ticker(request.GET.get("ticker", ""))
    if not code:
        return JsonResponse({"name": "", "market": "", "currency": ""})
    market, currency = detect_market(code)
    name = get_company_name(code, market)
    return JsonResponse({"ticker": code, "name": name, "market": market, "currency": currency})


@login_required
def export_csv(request):
    response = HttpResponse(content_type="text/csv; charset=utf-8-sig")
    response["Content-Disposition"] = 'attachment; filename="trades_export.csv"'
    response.write("\ufeff")
    writer = csv.writer(response)
    writer.writerow(["日付", "市場", "銘柄コード/Ticker", "銘柄名", "売買", "数量", "価格", "通貨", "手数料", "備考"])
    for t in Trade.objects.filter(user=request.user):
        writer.writerow([t.date.strftime("%Y-%m-%d %H:%M"), t.market, t.ticker, t.name,
                         t.side, t.quantity, t.price, t.currency, t.fee, t.note])
    return response