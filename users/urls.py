# users/urls.py
from django.urls import path
from .views import (SignInView, SignUpView, EmailVerificationView, 
                   CustomPasswordResetView, CustomPasswordResetConfirmView)

urlpatterns = [
    path('', SignInView.as_view(), name='signin'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('verify-email/<str:token>/', EmailVerificationView.as_view(), name='verify_email'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]