from django.contrib import admin
from .models import Trade


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ("date", "user", "ticker", "name", "side", "quantity", "price", "currency", "fee")
    list_filter = ("market", "side", "currency", "user")
    search_fields = ("ticker", "name", "note")
    date_hierarchy = "date"
    ordering = ("-date",)
    list_per_page = 50