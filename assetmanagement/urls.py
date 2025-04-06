from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("assets/", include("assets.urls")),
    path("", include("users.urls")),
]
