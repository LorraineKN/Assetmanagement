# users/views.py
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetView
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, FormView, TemplateView, View

from .forms import SignInForm, SignUpForm
from .models import User, UserActivity, UserSession


class SignInView(FormView):
    """Handle user authentication using email and password"""

    template_name = "users/signin.html"
    form_class = SignInForm
    success_url = reverse_lazy("user_dashboard")

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        remember_me = form.cleaned_data.get("remember_me")

        user = authenticate(self.request, email=email, password=password)

        if user is not None:
            if not user.is_active:
                messages.error(
                    self.request,
                    "Your account is inactive. Please contact an administrator.",
                )
                return self.form_invalid(form)

            if not user.email_verified:
                messages.warning(
                    self.request, "Please verify your email before signing in."
                )
                return self.form_invalid(form)

            # Login the user
            login(self.request, user)

            # Set session expiry based on remember_me
            if not remember_me:
                self.request.session.set_expiry(0)

            # Update last activity timestamp
            user.last_activity = timezone.now()
            user.save()

            # Log the user activity
            UserActivity.objects.create(
                user=user,
                activity_type="login",
                ip_address=self.request.META.get("REMOTE_ADDR"),
                user_agent=self.request.META.get("HTTP_USER_AGENT"),
                description="User logged in",
            )

            # Create user session record
            UserSession.objects.create(
                user=user,
                session_key=self.request.session.session_key,
                ip_address=self.request.META.get("REMOTE_ADDR"),
                user_agent=self.request.META.get("HTTP_USER_AGENT"),
            )

            # Determine where to redirect based on user_type
            if user.is_admin:
                self.success_url = reverse_lazy("admin_dashboard")
            elif user.is_manager:
                self.success_url = reverse_lazy("manager_dashboard")

            return super().form_valid(form)
        else:
            messages.error(self.request, "Invalid email or password.")
            return self.form_invalid(form)


class SignUpView(CreateView):
    """Handle user registration"""

    model = User
    form_class = SignUpForm
    template_name = "users/signup.html"
    success_url = reverse_lazy("signin")

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object

        # Generate and save verification token
        verification_token = user.generate_verification_token()

        # Build verification link
        verification_link = f"{settings.BASE_URL}/verify-email/{verification_token}/"

        # Email content
        subject = "Verify your email address"
        message = f"""
        Hi {user.first_name},
        
        Thank you for registering. Please click the link below to verify your email address:
        
        {verification_link}
        
        If you didn't request this, please ignore this email.
        """

        html_message = render_to_string(
            "emails/verification_email.html",
            {
                "user": user,
                "verification_link": verification_link,
                "site_name": settings.SITE_NAME,
            },
        )

        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        messages.success(
            self.request,
            "Registration successful! Please check your email to verify your account.",
        )
        return response


class EmailVerificationView(TemplateView):
    """Handle email verification"""

    template_name = "users/email_verified.html"

    def get(self, request, *args, **kwargs):
        token = kwargs.get("token")

        if not token or token == "None":
            messages.error(request, "Invalid verification link.")
            return redirect("signin")

        try:
            user = User.objects.get(verification_token=token)
            if not user.email_verified:
                user.email_verified = True
                user.verification_token = None
                user.save()
                messages.success(request, "Your email has been verified successfully!")
            else:
                messages.info(request, "Your email is already verified.")
        except User.DoesNotExist:
            messages.error(request, "Invalid verification token.")
            return redirect("signin")

        return super().get(request, *args, **kwargs)


class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view"""

    template_name = "users/password_reset.html"
    email_template_name = "emails/password_reset_email.html"
    subject_template_name = "users/password_reset_subject.txt"
    success_url = reverse_lazy("password_reset_done")


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Custom password reset confirmation view"""

    template_name = "users/password_reset_confirm.html"
    success_url = reverse_lazy("password_reset_complete")

class ResendVerificationView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Only resend if email isn't already verified
        if not user.email_verified:
            verification_token = user.generate_verification_token()
            verification_link = f"{settings.BASE_URL}/verify-email/{verification_token}/"
            
            # Send verification email
            subject = 'Verify your email address'
            html_message = render_to_string('emails/verification_email.html', {
                'user': user,
                'verification_link': verification_link,
                'site_name': settings.SITE_NAME
            })
            
            send_mail(
                subject=subject,
                message=f"Please verify your email: {verification_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            messages.success(request, 'Verification email has been resent. Please check your inbox.')
        else:
            messages.info(request, 'Your email is already verified.')
        
        return redirect('signin')

# class SignOutView(LoginRequiredMixin, RedirectView):
#     """Handle user sign out and log the activity"""
#     url = reverse_lazy('signin')

#     def get(self, request, *args, **kwargs):
#         if request.user.is_authenticated:
#             # Log the user activity
#             UserActivity.objects.create(
#                 user=request.user,
#                 activity_type='logout',
#                 ip_address=request.META.get('REMOTE_ADDR'),
#                 user_agent=request.META.get('HTTP_USER_AGENT'),
#                 description='User logged out'
#             )

#             # Update user session record
#             try:
#                 user_session = UserSession.objects.get(
#                     user=request.user,
#                     session_key=request.session.session_key,
#                     is_active=True
#                 )
#                 user_session.logout_time = timezone.now()
#                 user_session.is_active = False
#                 user_session.save()
#             except UserSession.DoesNotExist:
#                 pass

#         logout(request)
#         return super().get(request, *args, **kwargs)
