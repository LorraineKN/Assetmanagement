import secrets

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager to handle email as the unique identifier"""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("user_type", "ADMIN")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model with email as the unique identifier"""

    USER_TYPE_CHOICES = (
        ("ADMIN", "Administrator"),
        ("MANAGER", "Manager"),
        ("USER", "Regular User"),
    )

    username = None  # Remove username field
    email = models.EmailField(_("email address"), unique=True)
    user_type = models.CharField(
        max_length=20, choices=USER_TYPE_CHOICES, default="USER"
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(
        upload_to="profile_images/", blank=True, null=True
    )
    bio = models.TextField(blank=True, null=True)

    # For password reset
    reset_password_token = models.CharField(max_length=100, blank=True, null=True)
    reset_password_expires = models.DateTimeField(blank=True, null=True)

    # For email verification
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True)

    # Activity tracking
    last_activity = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_admin(self):
        return self.user_type == "ADMIN"

    @property
    def is_manager(self):
        return self.user_type == "MANAGER"

    def generate_verification_token(self):
        self.verification_token = secrets.token_urlsafe(32)
        self.save()
        return self.verification_token


class UserPreference(models.Model):
    """User preferences for application settings"""

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="preferences"
    )
    dark_mode = models.BooleanField(default=False)
    notifications_enabled = models.BooleanField(default=True)
    dashboard_widgets = models.JSONField(default=dict, blank=True, null=True)
    language = models.CharField(max_length=10, default="en")
    timezone = models.CharField(max_length=50, default="UTC")

    def __str__(self):
        return f"{self.user.email}'s preferences"


class UserNotification(models.Model):
    """User notifications model"""

    NOTIFICATION_TYPES = (
        ("system", "System"),
        ("asset", "Asset"),
        ("maintenance", "Maintenance"),
        ("transfer", "Transfer"),
        ("audit", "Audit"),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_object_id = models.CharField(max_length=50, blank=True, null=True)
    related_object_type = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.user.email}"

    class Meta:
        ordering = ["-created_at"]


class UserActivity(models.Model):
    """User activity logging"""

    ACTIVITY_TYPES = (
        ("login", "Login"),
        ("logout", "Logout"),
        ("view", "View"),
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("download", "Download"),
        ("export", "Export"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    module = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.activity_type} - {self.timestamp}"

    class Meta:
        verbose_name_plural = "User activities"
        ordering = ["-timestamp"]


class UserSession(models.Model):
    """User session tracking"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    session_key = models.CharField(max_length=40)
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.email} - {self.login_time}"
