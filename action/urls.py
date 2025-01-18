from django.urls import path

from action.views import ActionListView

urlpatterns = [
    path("create-action/", ActionListView.as_view({"patch": "create_action"})),
    path("get-action/", ActionListView.as_view({"get": "ge_all_action"})),
    path("get-action/<uuid:action_id>/", ActionListView.as_view({"get": "retrieve"})),
    path("update-action/<uuid:action_id>/", ActionListView.as_view({"patch": "update_action"})),
    path("delete-action/<uuid:action_id>/", ActionListView.as_view({"delete": "destroy"})),
    path("get-strategy-actions/<uuid:strategy_id>/", ActionListView.as_view({"get": "get_strategy_actions"})),
]
