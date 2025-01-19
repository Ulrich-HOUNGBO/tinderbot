from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="TINDER BOT API",
        default_version="v1.2",
        description="Welcome to TINDER BOT API Project",
        terms_of_service="",
        contact=openapi.Contact(email="info@serviceloop.co"),
        license=openapi.License(name=""),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path(
        "docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("api/", include("users.urls")),
    path("api/", include("bot.urls")),
    path("api/", include("account.urls")),
    path("api/", include("strategies.urls")),
    path("api/", include("proxies.urls")),
    path("api/", include("modeles.urls")),
    path("api/", include("action.urls")),
]
