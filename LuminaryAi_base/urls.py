# LuminaryAi_base\urls.py
from django.contrib import admin
from django.urls import path, include

app_name = "LuminaryAi_base"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("LuminaryAi_chat.urls")),
]
