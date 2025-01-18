from django.urls import path

from modeles.views import ModelesView
from proxies.urls import urlpatterns

urlpatterns = [
    path("create-modele/", ModelesView.as_view({"post": "create_modele"})),
    path("get-all-modele/", ModelesView.as_view({"get": "get_all_modele"})),
    path("get-modele/<uuid:modele_id>", ModelesView.as_view({"get": "get_modele"})),
    path(
        "update-modele/<uuid:modele_id>", ModelesView.as_view({"patch": "update_modele"})
    ),
    path(
        "delete-modele/<uuid:modele_id>", ModelesView.as_view({"delete": "delete_modele"})
    ),

]
