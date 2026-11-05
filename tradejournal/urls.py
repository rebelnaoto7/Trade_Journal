from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Django標準の認証（login, logout, password_change 等）
    # /accounts/login/  /accounts/logout/  が使えるようになる
    path("accounts/", include("django.contrib.auth.urls")),

    # ログイン後・ログアウト後のリダイレクト先を / にしたい場合の補助
    # （settings.py の LOGIN_URL / LOGIN_REDIRECT_URL と合わせて使う）

    # アプリ本体（trade_list, trade_create, analysis 等）
    path("", include("tracker.urls")),
]