from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import User


class SignInForm(forms.Form):
    """Form for user authentication"""

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email Address"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        )
    )
    remember_me = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        help_text="Required. Enter a valid email address.",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email Address"}
        ),
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "First Name"}
        ),
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Last Name"}
        ),
    )
    password1 = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        ),
    )
    password2 = forms.CharField(
        label=_("Password Confirmation"),
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm Password"}
        ),
    )

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with that email already exists.")
        return email
