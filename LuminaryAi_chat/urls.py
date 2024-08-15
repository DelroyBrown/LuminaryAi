# LuminaryAi_chat\urls.py
from django.urls import path
from .views import get_gpt_response, home

app_name = "LuminaryAi_chat"

urlpatterns = [
    path("", home, name="home"),
    path("api/get_gpt_response/", get_gpt_response, name="get_gpt_response"),
]
