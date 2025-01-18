from django.urls import path

from proxies.views import ProxiesView

urlpatterns = [
    path("create-proxy/", ProxiesView.as_view({"post": "create_proxy"})),
    path("get-all-proxy/", ProxiesView.as_view({"get": "get_all_proxy"})),
    path("get-proxy/<uuid:proxy_id>", ProxiesView.as_view({"get": "get_proxy"})),
    path(
        "update-proxy/<uuid:proxy_id>", ProxiesView.as_view({"patch": "update_proxy"})
    ),
    path(
        "test_proxy/<uuid:proxy_id>", ProxiesView.as_view({"patch": "test_proxy_connection"})
    ),
    path(
        "delete-proxy/<uuid:proxy_id>", ProxiesView.as_view({"delete": "delete_proxy"})
    ),
]
