from django.urls import path

from bot.views import BotSettingsView

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
