from __future__ import annotations
import csv
from datetime import datetime
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from tracker.models import Trade
from tracker.services import resolve_trade_fields


class Command(BaseCommand):
    help = "trades.csv を取り込む"

    def add_arguments(self, parser):
        parser.add_argument("csv_path")
        parser.add_argument("--user", required=True)
        parser.add_argument("--clear", action="store_true")

    def _parse_date(self, raw: str) -> datetime:
        raw = (raw or "").strip().replace("/", "-")
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(raw, fmt)
                return timezone.make_aware(dt) if timezone.is_naive(dt) else dt
            except ValueError:
                continue
        raise CommandError(f"日付を解釈できません: {raw!r}")

    @transaction.atomic
    def handle(self, *args, **opt):
        try:
            user = get_user_model().objects.get(username=opt["user"])
        except get_user_model().DoesNotExist:
            raise CommandError(f"ユーザー '{opt['user']}' が存在しません。")
        if opt["clear"]:
            deleted, _ = Trade.objects.filter(user=user).delete()
            self.stdout.write(self.style.WARNING(f"既存 {deleted} 件を削除しました。"))
        created = 0
        with open(opt["csv_path"], encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                code = row.get("銘柄コード/Ticker", "")
                if not code.strip():
                    continue
                r = resolve_trade_fields(code, row.get("銘柄名", ""))
                Trade.objects.create(
                    user=user, date=self._parse_date(row.get("日付", "")),
                    market=row.get("市場") or r["market"], ticker=r["ticker"], name=r["name"],
                    side=row.get("売買", "").strip(), quantity=row.get("数量") or 0,
                    price=row.get("価格") or 0, currency=row.get("通貨") or r["currency"],
                    fee=row.get("手数料") or 0, note=row.get("備考", ""))
                created += 1
        self.stdout.write(self.style.SUCCESS(f"取り込み完了: {created} 件"))