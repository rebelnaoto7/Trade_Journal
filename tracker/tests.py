from __future__ import annotations
from datetime import datetime
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from .analytics import calculate_stats
from .models import Trade
from .services import detect_market, normalize_ticker


class DetectMarketTests(TestCase):
    def test_jp_4digit(self):
        self.assertEqual(detect_market("7203"), ("日本株", "JPY"))
    def test_jp_new_format(self):
        self.assertEqual(detect_market("130A"), ("日本株", "JPY"))
        self.assertEqual(detect_market("130a"), ("日本株", "JPY"))
    def test_us(self):
        self.assertEqual(detect_market("AAPL"), ("米国株", "USD"))
        self.assertEqual(detect_market("msft"), ("米国株", "USD"))
    def test_normalize(self):
        self.assertEqual(normalize_ticker("  aapl "), "AAPL")


class AnalyticsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user("tester", password="x")
    def _make(self, ticker, side, qty, price, fee=0, market="日本株", currency="JPY", day=1):
        return Trade.objects.create(user=self.user, ticker=ticker, name=ticker, side=side,
            quantity=qty, price=price, fee=fee, market=market, currency=currency,
            date=timezone.make_aware(datetime(2026, 4, day, 9, 0)))
    def test_realized_pnl_average_cost(self):
        self._make("7203", "買", 100, 4000, 1000, day=1)
        self._make("7203", "売", 100, 4500, 1000, day=2)
        self._make("7203", "買", 100, 3392, 1000, day=3)
        self._make("7203", "売", 100, 3380, 1000, day=4)
        stats = calculate_stats(Trade.objects.filter(user=self.user))
        self.assertEqual(stats["jpy"]["total_pnl"], 44800.0)
        self.assertEqual(stats["jpy"]["win_rate"], 100.0)
        self.assertIsNone(stats["jpy"]["pf"])
    def test_open_position_excluded(self):
        self._make("2222", "買", 100, 2000, day=1)
        stats = calculate_stats(Trade.objects.filter(user=self.user))
        self.assertEqual(stats["jpy"]["count"], 0)
        self.assertEqual(len(stats["open_jpy"]), 1)
        self.assertEqual(stats["open_jpy"][0]["qty"], 100)
    def test_partial_sell(self):
        self._make("9999", "買", 200, 1000, day=1)
        self._make("9999", "売", 100, 1200, day=2)
        stats = calculate_stats(Trade.objects.filter(user=self.user))
        self.assertEqual(stats["jpy"]["total_pnl"], 20000.0)
        self.assertEqual(stats["open_jpy"][0]["qty"], 100)
    def test_currency_separation(self):
        self._make("AAPL", "買", 10, 100, market="米国株", currency="USD", day=1)
        self._make("AAPL", "売", 10, 120, market="米国株", currency="USD", day=2)
        stats = calculate_stats(Trade.objects.filter(user=self.user))
        self.assertEqual(stats["usd"]["total_pnl"], 200.0)
        self.assertEqual(stats["jpy"]["count"], 0)
    def test_empty(self):
        self.assertIsNone(calculate_stats([]))


class ViewSecurityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        U = get_user_model()
        cls.alice = U.objects.create_user("alice", password="x")
        cls.bob = U.objects.create_user("bob", password="x")
        cls.t = Trade.objects.create(user=cls.alice, ticker="7203", name="Toyota", side="買",
            quantity=100, price=4000, market="日本株", currency="JPY", date=timezone.now())
    def test_login_required(self):
        self.assertEqual(self.client.get("/").status_code, 302)
    def test_user_isolation(self):
        self.client.login(username="bob", password="x")
        resp = self.client.post(f"/{self.t.pk}/delete/")
        self.assertEqual(resp.status_code, 404)
        self.assertTrue(Trade.objects.filter(pk=self.t.pk).exists())