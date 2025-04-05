from django.contrib.auth import views as auth_views
from django.urls import path

urlpatterns = [
    path(
        "signin/",
        auth_views.LoginView.as_view(template_name="assets/signin.html"),
        name="signin",
    ),
]
