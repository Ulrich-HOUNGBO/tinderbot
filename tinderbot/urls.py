"""
URL configuration for tinderbot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("create-bot-settings/", BotSettingsView.as_view({"patch": "create_settings"})),
    path(
        "get-settings",
        BotSettingsView.as_view({"get": "get_settings"}),
    ),
    path(
        "get-settings-strategy/<uuid:strategy_id>",
        BotSettingsView.as_view({"get": "get_settings_strategy"}),
    ),
    path(
        "update-bot-settings/<uuid:bot_settings_id>",
        BotSettingsView.as_view({"patch": "update_settings"}),
    ),
    path(
        "delete-bot-settings/<uuid:bot_settings_id>",
        BotSettingsView.as_view({"delete": "delete_settings"}),
    ),
    path(
        "start-bot/<uuid:bot_settings_id>",
        BotSettingsView.as_view({"patch": "start_bot"}),
    ),
    path(
        "stop-bot/<uuid:bot_settings_id>",
        BotSettingsView.as_view({"patch": "stop_bot"}),
    ),
    path(
        "get-token/",
        BotSettingsView.as_view({"get": "get_tinder_auth_token"}),
    ),
]
