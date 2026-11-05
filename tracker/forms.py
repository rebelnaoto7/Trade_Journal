from __future__ import annotations
from django import forms
from django.utils import timezone
from .models import Trade


class TradeForm(forms.ModelForm):
    date = forms.DateTimeField(
        label="約定日時",
        initial=lambda: timezone.localtime().strftime("%Y-%m-%dT%H:%M"),
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "input"}, format="%Y-%m-%dT%H:%M"),
        input_formats=["%Y-%m-%dT%H:%M"],
    )
    quantity = forms.DecimalField(label="数量", min_value=0,
        widget=forms.NumberInput(attrs={"placeholder": "例: 100", "step": "1", "min": "0", "inputmode": "numeric", "class": "input input--num"}))
    price = forms.DecimalField(label="価格", min_value=0,
        widget=forms.NumberInput(attrs={"placeholder": "例: 4000", "step": "0.01", "min": "0", "inputmode": "decimal", "class": "input input--num"}))
    fee = forms.DecimalField(label="手数料", required=False, min_value=0, initial=0,
        widget=forms.NumberInput(attrs={"placeholder": "0", "step": "1", "min": "0", "inputmode": "numeric", "class": "input input--num"}))

    class Meta:
        model = Trade
        fields = ["date", "side", "ticker", "name", "quantity", "price", "fee", "note"]
        widgets = {
            "side": forms.Select(attrs={"class": "input"}),
            "ticker": forms.TextInput(attrs={"placeholder": "例: 7203 / AAPL", "class": "input input--ticker", "autocomplete": "off", "autofocus": True}),
            "name": forms.TextInput(attrs={"placeholder": "空欄で自動取得", "class": "input"}),
            "note": forms.Textarea(attrs={"rows": 2, "placeholder": "（任意）メモ・根拠など", "class": "input"}),
        }
        labels = {"side": "売買", "ticker": "銘柄コード/Ticker", "name": "銘柄名", "note": "備考"}

    def clean_fee(self):
        return self.cleaned_data.get("fee") or 0