from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("assets/", include("assets.urls", namespace="assets")),
    path("", include("users.urls")),
]


admin.site.site_header = "AssetFlow Management Administration"
admin.site.site_title = "AssetFlow Management"
admin.site.index_title = "AssetFlow Management Dashboard"