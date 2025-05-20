from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import (
    AssetCreateView,
    AssetDeleteView,
    AssetDetailView,
    AssetListView,
    AssetUpdateView,
    AuditLogListView,
    CustodianListView,
    DashboardView,
    DepartmentListView,
    LocationListView,
    MaintenanceCreateView,
    MaintenanceDeleteView,
    MaintenanceDetailView,
    MaintenanceListView,
    MaintenanceUpdateView,
    VendorListView,
)

app_name = "assets"

urlpatterns = [
    # Dashboard
    path("dashboard/", login_required(DashboardView.as_view()), name="dashboard"),
    # Asset URLs
    path("assets/", login_required(AssetListView.as_view()), name="asset_list"),
    path(
        "assets/create/", login_required(AssetCreateView.as_view()), name="asset_create"
    ),
    path(
        "assets/<int:pk>/",
        login_required(AssetDetailView.as_view()),
        name="asset_detail",
    ),
    path(
        "assets/<int:pk>/update/",
        login_required(AssetUpdateView.as_view()),
        name="asset_update",
    ),
    path(
        "assets/<int:pk>/delete/",
        login_required(AssetDeleteView.as_view()),
        name="asset_delete",
    ),
    # Maintenance URLs
    path(
        "maintenance/",
        login_required(MaintenanceListView.as_view()),
        name="maintenance_list",
    ),
    path(
        "maintenance/create/",
        login_required(MaintenanceCreateView.as_view()),
        name="maintenance_create",
    ),
    path(
        "maintenance/<int:pk>/",
        login_required(MaintenanceDetailView.as_view()),
        name="maintenance_detail",
    ),
    path(
        "maintenance/<int:pk>/update/",
        login_required(MaintenanceUpdateView.as_view()),
        name="maintenance_update",
    ),
    path(
        "maintenance/<int:pk>/delete/",
        login_required(MaintenanceDeleteView.as_view()),
        name="maintenance_delete",
    ),
    # Audit Log URLs
    path("audit-logs/", login_required(AuditLogListView.as_view()), name="audit_logs"),
    # Other List Views
    path("vendors/", login_required(VendorListView.as_view()), name="vendor_list"),
    path(
        "departments/",
        login_required(DepartmentListView.as_view()),
        name="department_list",
    ),
    path(
        "locations/", login_required(LocationListView.as_view()), name="location_list"
    ),
    path(
        "custodians/",
        login_required(CustodianListView.as_view()),
        name="custodian_list",
    ),
]
