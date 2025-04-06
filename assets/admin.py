from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html

from .models import (Asset, AssetTransfer, AuditLog, Category, Custodian,
                     Department, DepreciationRecord, FinancialTransaction,
                     Location, MaintenanceRecord, Tag, Vendor)


class BaseAdmin(admin.ModelAdmin):
    """Base admin class with common fields and behaviors"""

    readonly_fields = ("created_at", "updated_at", "created_by", "updated_by")
    list_filter = ("created_at", "updated_at")
    date_hierarchy = "created_at"

    def save_model(self, request, obj, form, change):
        """Track who created or updated the record"""
        if not obj.id:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Department)
class DepartmentAdmin(BaseAdmin):
    list_display = ("name", "code", "parent", "get_children_count")
    search_fields = ("name", "code", "description")
    list_filter = ("parent", *BaseAdmin.list_filter)

    def get_children_count(self, obj):
        return obj.children.count()

    get_children_count.short_description = "Subdepartments"


@admin.register(Location)
class LocationAdmin(BaseAdmin):
    list_display = ("name", "building", "room", "department")
    search_fields = ("name", "building", "room", "address")
    list_filter = ("building", "department", *BaseAdmin.list_filter)


@admin.register(Custodian)
class CustodianAdmin(BaseAdmin):
    list_display = ("user", "department", "is_active")
    search_fields = ("user__username", "user__first_name", "user__last_name")
    list_filter = ("is_active", "department", *BaseAdmin.list_filter)
    autocomplete_fields = ["user", "department"]


@admin.register(Vendor)
class VendorAdmin(BaseAdmin):
    list_display = ("name", "contact_person", "email", "phone", "is_active")
    search_fields = ("name", "contact_person", "email", "tax_id")
    list_filter = ("is_active", *BaseAdmin.list_filter)


@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    list_display = ("name", "parent", "get_subcategories_count")
    search_fields = ("name", "description")
    list_filter = ("parent", *BaseAdmin.list_filter)

    def get_subcategories_count(self, obj):
        return obj.subcategories.count()

    get_subcategories_count.short_description = "Subcategories"


@admin.register(Tag)
class TagAdmin(BaseAdmin):
    list_display = ("name", "colored_tag", "get_assets_count")
    search_fields = ("name",)

    def colored_tag(self, obj):
        return format_html(
            '<span style="background-color: {}; color: #fff; padding: 3px 7px; border-radius: 3px;">{}</span>',
            obj.color,
            obj.name,
        )

    colored_tag.short_description = "Tag"

    def get_assets_count(self, obj):
        return obj.asset_set.count()

    get_assets_count.short_description = "Assets"


class MaintenanceRecordInline(admin.TabularInline):
    model = MaintenanceRecord
    extra = 0
    fields = ("maintenance_type", "status", "schedule_date", "completion_date", "cost")


class AssetTransferInline(admin.TabularInline):
    model = AssetTransfer
    extra = 0
    fields = (
        "from_location",
        "to_location",
        "from_custodian",
        "to_custodian",
        "transfer_date",
    )
    fk_name = "asset"


class DepreciationRecordInline(admin.TabularInline):
    model = DepreciationRecord
    extra = 0
    fields = ("record_date", "value_before", "value_after", "depreciation_amount")


@admin.register(Asset)
class AssetAdmin(BaseAdmin):
    list_display = (
        "asset_id",
        "name",
        "status",
        "category",
        "location",
        "custodian",
        "purchase_date",
        "current_value",
        "last_audited",
    )
    list_filter = (
        "status",
        "category",
        "location",
        "custodian",
        "purchase_date",
        "last_audited",
        *BaseAdmin.list_filter,
    )
    search_fields = ("asset_id", "name", "description", "serial_number", "model_number")
    readonly_fields = (*BaseAdmin.readonly_fields, "current_value")
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "asset_id",
                    "name",
                    "description",
                    "status",
                    "category",
                    "tags",
                    "image",
                )
            },
        ),
        (
            "Technical Details",
            {"fields": ("serial_number", "model_number", "manufacturer")},
        ),
        (
            "Financial Information",
            {
                "fields": (
                    "purchase_price",
                    "current_value",
                    "purchase_date",
                    "purchase_order",
                    "warranty_expiry_date",
                    "expected_life_years",
                    "depreciation_rate",
                )
            },
        ),
        (
            "Assignment Information",
            {"fields": ("vendor", "location", "custodian", "last_audited", "notes")},
        ),
        (
            "System Fields",
            {
                "classes": ("collapse",),
                "fields": ("created_at", "updated_at", "created_by", "updated_by"),
            },
        ),
    )
    filter_horizontal = ("tags",)
    inlines = [MaintenanceRecordInline, AssetTransferInline, DepreciationRecordInline]
    autocomplete_fields = ["category", "vendor", "location", "custodian"]

    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related"""
        return (
            super()
            .get_queryset(request)
            .select_related("category", "vendor", "location", "custodian")
            .prefetch_related("tags")
        )


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(BaseAdmin):
    list_display = (
        "asset",
        "maintenance_type",
        "status",
        "schedule_date",
        "completion_date",
        "cost",
    )
    list_filter = (
        "maintenance_type",
        "status",
        "schedule_date",
        "completion_date",
        *BaseAdmin.list_filter,
    )
    search_fields = ("asset__name", "asset__asset_id", "description", "findings")
    autocomplete_fields = ["asset", "service_provider"]


@admin.register(AssetTransfer)
class AssetTransferAdmin(BaseAdmin):
    list_display = (
        "asset",
        "from_location",
        "to_location",
        "from_custodian",
        "to_custodian",
        "transfer_date",
    )
    list_filter = (
        "transfer_date",
        "from_location",
        "to_location",
        *BaseAdmin.list_filter,
    )
    search_fields = ("asset__name", "asset__asset_id", "reason")
    autocomplete_fields = [
        "asset",
        "from_location",
        "to_location",
        "from_custodian",
        "to_custodian",
        "approved_by",
    ]


@admin.register(DepreciationRecord)
class DepreciationRecordAdmin(BaseAdmin):
    list_display = (
        "asset",
        "record_date",
        "value_before",
        "value_after",
        "depreciation_amount",
    )
    list_filter = ("record_date", *BaseAdmin.list_filter)
    search_fields = ("asset__name", "asset__asset_id")
    autocomplete_fields = ["asset"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "timestamp",
        "user",
        "action",
        "model_name",
        "object_id",
        "ip_address",
    )
    list_filter = ("action", "model_name", "timestamp", "user")
    search_fields = ("user__username", "model_name", "object_id", "details")
    readonly_fields = (
        "timestamp",
        "user",
        "action",
        "model_name",
        "object_id",
        "details",
        "ip_address",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(FinancialTransaction)
class FinancialTransactionAdmin(BaseAdmin):
    list_display = (
        "transaction_type",
        "amount",
        "date",
        "asset",
        "vendor",
        "reference_number",
    )
    list_filter = ("transaction_type", "date", "vendor", *BaseAdmin.list_filter)
    search_fields = (
        "description",
        "reference_number",
        "asset__name",
        "asset__asset_id",
    )
    autocomplete_fields = ["asset", "vendor"]


# Optional: Custom admin index with statistics
class AssetManagementAdminSite(admin.AdminSite):
    """Custom admin site with dashboard"""

    def get_app_list(self, request):
        """Add asset statistics to the admin index"""
        app_list = super().get_app_list(request)

        try:
            # Get some statistics
            total_assets = Asset.objects.count()
            active_assets = Asset.objects.filter(status="active").count()
            total_value = (
                Asset.objects.aggregate(Sum("current_value"))["current_value__sum"] or 0
            )
            pending_maintenance = MaintenanceRecord.objects.filter(
                status__in=["scheduled", "in_progress"]
            ).count()

            # Add stats to the app_list
            for app in app_list:
                if (
                    app.get("app_label") == "your_app_name"
                ):  # Replace with your actual app name
                    app["stats"] = {
                        "total_assets": total_assets,
                        "active_assets": active_assets,
                        "total_value": total_value,
                        "pending_maintenance": pending_maintenance,
                    }
        except:
            # Gracefully handle any errors
            pass

        return app_list
