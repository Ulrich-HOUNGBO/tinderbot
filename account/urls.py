from django.urls import path

from account.views import AccountViews

urlpatterns = [
    path("create-account/", AccountViews.as_view({"post": "create_account"})),
    path("get-accounts/", AccountViews.as_view({"get": "get_all_account"})),
    path(
        "get-account/<uuid:account_id>",
        AccountViews.as_view({"get": "get_account"}),
    ),
    path(
        "update-account/<uuid:account_id>",
        AccountViews.as_view({"patch": "update_account"}),
    ),
    path(
        "reset-process/<uuid:account_id>",
        AccountViews.as_view({"patch": "reset_process"}),
    ),
    path(
        "add-bio/<uuid:account_id>",
        AccountViews.as_view({"patch": "add_bio"}),
    ),
    path(
        "start-process/<uuid:account_id>",
        AccountViews.as_view({"patch": "start_process"}),
    ),
    path(
        "delete-account/<uuid:account_id>",
        AccountViews.as_view({"delete": "delete_account"}),
    ),
    path(
        "automate_process",
        AccountViews.as_view({"get": "automate_all_account_process"}),
    ),

    path(
        "test-account/<uuid:accoun_id>",
        AccountViews.as_view({"post": "test_account"}),
    ),
]
