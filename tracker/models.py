from __future__ import annotations
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Market(models.TextChoices):
    JP = "日本株", "日本株"
    US = "米国株", "米国株"


class Side(models.TextChoices):
    BUY = "買", "買"
    SELL = "売", "売"


class Currency(models.TextChoices):
    JPY = "JPY", "JPY"
    USD = "USD", "USD"


class Trade(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="trades")
    date = models.DateTimeField("約定日時", default=timezone.now, db_index=True)
    market = models.CharField("市場", max_length=10, choices=Market.choices)
    ticker = models.CharField("銘柄コード/Ticker", max_length=20, db_index=True)
    name = models.CharField("銘柄名", max_length=200, blank=True)
    side = models.CharField("売買", max_length=2, choices=Side.choices)
    quantity = models.DecimalField("数量", max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    price = models.DecimalField("価格", max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])
    currency = models.CharField("通貨", max_length=5, choices=Currency.choices)
    fee = models.DecimalField("手数料", max_digits=15, decimal_places=2, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))])
    note = models.TextField("備考", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-id"]
        indexes = [
            models.Index(fields=["user", "-date"]),
            models.Index(fields=["user", "ticker"]),
        ]

    def __str__(self) -> str:
        return f"{self.date:%Y-%m-%d} {self.ticker} {self.side} {self.quantity}@{self.price}"

    @property
    def gross_amount(self) -> Decimal:
        return self.quantity * self.price

    @property
    def is_buy(self) -> bool:
        return self.side == Side.BUY