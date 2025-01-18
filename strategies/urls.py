from django.urls import path

from strategies.views import StrategyViews

urlpatterns = [
    path("create-strategy/", StrategyViews.as_view({"post": "create_strategy"})),
    path("get-strategy/", StrategyViews.as_view({"get": "get_all_strategy"})),
    path(
        "get-strategy/<uuid:strategy_id>",
        StrategyViews.as_view({"get": "get_strategy"}),
    ),
    path(
        "update-strategy/<uuid:strategy_id>",
        StrategyViews.as_view({"patch": "update_strategy"}),
    ),
    path(
        "delete-strategy/<uuid:strategy_id>",
        StrategyViews.as_view({"delete": "delete_strategy"}),
    ),
]
