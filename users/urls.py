# users/urls.py
from django.urls import path

from .views import (CustomPasswordResetConfirmView, CustomPasswordResetView,
                    EmailVerificationView, HomePageView,
                    ResendVerificationView, SignInView, SignUpView)

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("sigin", SignInView.as_view(), name="signin"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path(
        "verify-email/<str:token>/",
        EmailVerificationView.as_view(),
        name="verify_email",
    ),
    path("password-reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "resend-verification/",
        ResendVerificationView.as_view(),
        name="resend_verification",
    ),
]
