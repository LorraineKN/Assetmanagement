from django.contrib import admin

from .models import Asset, Category, Custodian, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Custodian)
class CustodianAdmin(admin.ModelAdmin):
    list_display = ("user", "department")


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "purchase_date",
        "availability",
        "custodian",
    )
    list_filter = ("category", "availability")
    search_fields = ("name", "description")
