from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, UserPreference, UserNotification, UserActivity, UserSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "user_type",
        "is_active",
        "is_staff",
        "last_login",
    )
    list_filter = (
        "user_type",
        "is_active",
        "is_staff",
        "is_superuser",
        "email_verified",
    )
    search_fields = ("email", "first_name", "last_name", "phone_number")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                    "profile_image",
                    "bio",
                )
            },
        ),
        (_("User type"), {"fields": ("user_type",)}),
        (_("Verification"), {"fields": ("email_verified", "verification_token")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Important dates"),
            {"fields": ("last_login", "date_joined", "last_activity")},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "user_type",
                ),
            },
        ),
    )


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "dark_mode",
        "notifications_enabled",
        "language",
        "timezone",
    )
    list_filter = ("dark_mode", "notifications_enabled", "language")
    search_fields = ("user__email", "user__first_name", "user__last_name")


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("user__email", "title", "message")
    date_hierarchy = "created_at"


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ("user", "activity_type", "timestamp", "ip_address", "module")
    list_filter = ("activity_type", "timestamp")
    search_fields = ("user__email", "description", "module")
    date_hierarchy = "timestamp"
    readonly_fields = (
        "user",
        "activity_type",
        "timestamp",
        "ip_address",
        "user_agent",
        "module",
        "description",
    )


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "login_time", "logout_time", "ip_address", "is_active")
    list_filter = ("is_active", "login_time")
    search_fields = ("user__email", "session_key", "ip_address")
    date_hierarchy = "login_time"
    readonly_fields = ("user", "session_key", "login_time", "ip_address", "user_agent")
