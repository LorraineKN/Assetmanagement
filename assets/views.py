from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import  Q, Sum
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  TemplateView, UpdateView)

from users.models import User

from .models import (Asset, AuditLog, Category, Custodian, Department,
                     Location, MaintenanceRecord, Vendor)


class DashboardView(TemplateView):
    """
    Class-based view for the asset management dashboard.
    Displays key metrics, charts, and recent activities.
    """

    template_name = "assets/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        # Total assets count
        context["total_assets"] = Asset.objects.count()

        # Pending maintenance count
        context["maintenance_count"] = MaintenanceRecord.objects.filter(
            status__in=["scheduled", "in_progress"]
        ).count()

        # Assets with warranty expiring within 30 days
        thirty_days = today + timezone.timedelta(days=30)
        context["warranty_expiring"] = Asset.objects.filter(
            warranty_expiry_date__isnull=False,
            warranty_expiry_date__gt=today,
            warranty_expiry_date__lte=thirty_days,
        ).count()

        # Total asset value
        total_value = Asset.objects.aggregate(total=Sum("current_value"))
        context["total_value"] = total_value["total"] or 0

        # Asset status distribution for pie chart
        context["status_counts"] = {
            "active": Asset.objects.filter(status="active").count(),
            "inactive": Asset.objects.filter(status="inactive").count(),
            "maintenance": Asset.objects.filter(status="maintenance").count(),
            "lost": Asset.objects.filter(status="lost").count(),
            "stolen": Asset.objects.filter(status="stolen").count(),
            "disposed": Asset.objects.filter(status="disposed").count(),
        }

        # Department values for bar chart
        departments = Department.objects.all()
        dept_values = []
        for dept in departments:
            dept_value = Asset.objects.filter(
                Q(location__department=dept) | Q(custodian__department=dept)
            ).aggregate(total_value=Sum("current_value"))

            dept_values.append(
                {"name": dept.name, "total_value": dept_value["total_value"] or 0}
            )

        context["dept_values"] = dept_values

        # Recent activities/logs
        context["recent_logs"] = AuditLog.objects.all().order_by("-timestamp")[:5]

        # Upcoming maintenance
        context["upcoming_maintenance"] = MaintenanceRecord.objects.filter(
            status__in=["scheduled", "in_progress"], schedule_date__gte=today
        ).order_by("schedule_date")[:5]

        context["today"] = today.strftime("%Y-%m-%d")

        return context


class AssetListView(LoginRequiredMixin, ListView):
    """
    View to display a list of all assets with filtering capabilities.
    """

    model = Asset
    template_name = "assets/asset_list.html"
    context_object_name = "assets"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        # Get filter parameters from request
        status = self.request.GET.get("status")
        category = self.request.GET.get("category")
        department = self.request.GET.get("department")
        search = self.request.GET.get("search")

        # Apply filters if provided
        if status:
            queryset = queryset.filter(status=status)
        if category:
            queryset = queryset.filter(category_id=category)
        if department:
            queryset = queryset.filter(
                Q(location__department_id=department)
                | Q(custodian__department_id=department)
            )
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(asset_id__icontains=search)
                | Q(serial_number__icontains=search)
            )

        return queryset.order_by("-updated_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add filter options to context
        context["categories"] = Category.objects.all()
        context["departments"] = Department.objects.all()
        context["statuses"] = dict(Asset.ASSET_STATUS)
        return context


class AssetDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying detailed information about an asset.
    """

    model = Asset
    template_name = "assets/asset_detail.html"
    context_object_name = "asset"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        asset = self.get_object()

        # Get related records
        context["maintenance_records"] = asset.maintenance_records.all().order_by(
            "-created_at"
        )[:5]
        context["transfers"] = asset.transfers.all().order_by("-transfer_date")[:5]
        context["depreciations"] = asset.depreciations.all().order_by("-record_date")[
            :5
        ]

        # Get audit logs for this asset
        context["audit_logs"] = AuditLog.objects.filter(
            model_name="Asset", object_id=str(asset.id)
        ).order_by("-timestamp")[:10]

        return context


class AssetCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new asset.
    """

    model = Asset
    template_name = "assets/asset_form.html"
    fields = [
        "name",
        "asset_id",
        "description",
        "category",
        "tags",
        "status",
        "serial_number",
        "model_number",
        "manufacturer",
        "purchase_price",
        "purchase_date",
        "purchase_order",
        "warranty_expiry_date",
        "expected_life_years",
        "depreciation_rate",
        "vendor",
        "location",
        "custodian",
        "image",
        "notes",
    ]
    success_url = reverse_lazy("assets:asset_list")

    def form_valid(self, form):
        # Set created_by to current user
        form.instance.created_by = self.request.user
        response = super().form_valid(form)

        # Create audit log
        AuditLog.objects.create(
            user=self.request.user,
            action="create",
            model_name="Asset",
            object_id=str(self.object.id),
            details={"name": self.object.name},
            ip_address=self.request.META.get("REMOTE_ADDR"),
        )

        return response


class AssetUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating an existing asset.
    """

    model = Asset
    template_name = "assets/asset_form.html"
    fields = [
        "name",
        "asset_id",
        "description",
        "category",
        "tags",
        "status",
        "serial_number",
        "model_number",
        "manufacturer",
        "purchase_price",
        "current_value",
        "purchase_date",
        "purchase_order",
        "warranty_expiry_date",
        "expected_life_years",
        "depreciation_rate",
        "vendor",
        "location",
        "custodian",
        "image",
        "notes",
    ]

    def get_success_url(self):
        return reverse_lazy("assets:asset_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        # Set updated_by to current user
        form.instance.updated_by = self.request.user
        response = super().form_valid(form)

        # Create audit log
        AuditLog.objects.create(
            user=self.request.user,
            action="update",
            model_name="Asset",
            object_id=str(self.object.id),
            details={"name": self.object.name},
            ip_address=self.request.META.get("REMOTE_ADDR"),
        )

        return response


class AssetDeleteView(LoginRequiredMixin, DeleteView):
    """
    View for deleting an asset.
    """

    model = Asset
    template_name = "assets/asset_confirm_delete.html"
    success_url = reverse_lazy("assets:asset_list")
    context_object_name = "asset"

    def delete(self, request, *args, **kwargs):
        asset = self.get_object()

        # Create audit log
        AuditLog.objects.create(
            user=self.request.user,
            action="delete",
            model_name="Asset",
            object_id=str(asset.id),
            details={"name": asset.name},
            ip_address=self.request.META.get("REMOTE_ADDR"),
        )

        return super().delete(request, *args, **kwargs)


# Maintenance Views
class MaintenanceListView(LoginRequiredMixin, ListView):
    """
    View to display a list of all maintenance records.
    """

    model = MaintenanceRecord
    template_name = "maintenance/maintenance_list.html"
    context_object_name = "maintenance_records"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()

        # Get filter parameters
        status = self.request.GET.get("status")
        maintenance_type = self.request.GET.get("type")
        search = self.request.GET.get("search")

        # Apply filters
        if status:
            queryset = queryset.filter(status=status)
        if maintenance_type:
            queryset = queryset.filter(maintenance_type=maintenance_type)
        if search:
            queryset = queryset.filter(
                Q(asset__name__icontains=search)
                | Q(asset__asset_id__icontains=search)
                | Q(description__icontains=search)
            )

        return queryset.order_by("-schedule_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = dict(MaintenanceRecord.STATUS_CHOICES)
        context["types"] = dict(MaintenanceRecord.MAINTENANCE_TYPES)
        return context


class MaintenanceDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying detailed information about a maintenance record.
    """

    model = MaintenanceRecord
    template_name = "maintenance/maintenance_detail.html"
    context_object_name = "maintenance"


class MaintenanceCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new maintenance record.
    """

    model = MaintenanceRecord
    template_name = "maintenance/maintenance_form.html"
    fields = [
        "asset",
        "maintenance_type",
        "status",
        "schedule_date",
        "completion_date",
        "cost",
        "service_provider",
        "description",
        "findings",
        "actions_taken",
        "next_maintenance_date",
    ]
    success_url = reverse_lazy("assets:maintenance_list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)

        # If status is in_progress, update asset status
        if form.instance.status == "in_progress":
            asset = form.instance.asset
            asset.status = "maintenance"
            asset.save()

        # Create audit log
        AuditLog.objects.create(
            user=self.request.user,
            action="create",
            model_name="MaintenanceRecord",
            object_id=str(self.object.id),
            details={"asset": self.object.asset.name},
            ip_address=self.request.META.get("REMOTE_ADDR"),
        )

        return response


class MaintenanceUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating a maintenance record.
    """

    model = MaintenanceRecord
    template_name = "maintenance/maintenance_form.html"
    fields = [
        "maintenance_type",
        "status",
        "schedule_date",
        "completion_date",
        "cost",
        "service_provider",
        "description",
        "findings",
        "actions_taken",
        "next_maintenance_date",
    ]

    def get_success_url(self):
        return reverse_lazy("assets:maintenance_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        old_status = MaintenanceRecord.objects.get(pk=self.object.pk).status
        response = super().form_valid(form)

        # Update asset status based on maintenance status changes
        asset = form.instance.asset
        if form.instance.status == "in_progress" and old_status != "in_progress":
            asset.status = "maintenance"
            asset.save()
        elif form.instance.status == "completed" and old_status == "in_progress":
            asset.status = "active"
            asset.save()

        # Create audit log
        AuditLog.objects.create(
            user=self.request.user,
            action="update",
            model_name="MaintenanceRecord",
            object_id=str(self.object.id),
            details={"asset": self.object.asset.name, "status": self.object.status},
            ip_address=self.request.META.get("REMOTE_ADDR"),
        )

        return response


class MaintenanceDeleteView(LoginRequiredMixin, DeleteView):
    """
    View for deleting a maintenance record.
    """

    model = MaintenanceRecord
    template_name = "maintenance/maintenance_confirm_delete.html"
    success_url = reverse_lazy("assets:maintenance_list")
    context_object_name = "maintenance"

    def delete(self, request, *args, **kwargs):
        maintenance = self.get_object()

        # Create audit log
        AuditLog.objects.create(
            user=self.request.user,
            action="delete",
            model_name="MaintenanceRecord",
            object_id=str(maintenance.id),
            details={"asset": maintenance.asset.name},
            ip_address=self.request.META.get("REMOTE_ADDR"),
        )

        return super().delete(request, *args, **kwargs)


# Audit Log Views
class AuditLogListView(LoginRequiredMixin, ListView):
    """
    View to display a list of all audit logs with filtering capabilities.
    """

    model = AuditLog
    template_name = "audit/audit_log_list.html"
    context_object_name = "logs"
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset()

        # Get filter parameters
        action = self.request.GET.get("action")
        model = self.request.GET.get("model")
        user_id = self.request.GET.get("user")
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")

        # Apply filters
        if action:
            queryset = queryset.filter(action=action)
        if model:
            queryset = queryset.filter(model_name=model)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)

        return queryset.order_by("-timestamp")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["actions"] = dict(AuditLog.ACTION_CHOICES)
        context["models"] = AuditLog.objects.values_list(
            "model_name", flat=True
        ).distinct()
        context["users"] = User.objects.all()
        return context


# Other List Views
class VendorListView(LoginRequiredMixin, ListView):
    """
    View to display a list of all vendors.
    """

    model = Vendor
    template_name = "vendors/vendor_list.html"
    context_object_name = "vendors"
    paginate_by = 20


class DepartmentListView(LoginRequiredMixin, ListView):
    """
    View to display a list of all departments.
    """

    model = Department
    template_name = "departments/department_list.html"
    context_object_name = "departments"


class LocationListView(LoginRequiredMixin, ListView):
    """
    View to display a list of all locations.
    """

    model = Location
    template_name = "locations/location_list.html"
    context_object_name = "locations"
    paginate_by = 20


class CustodianListView(LoginRequiredMixin, ListView):
    """
    View to display a list of all custodians.
    """

    model = Custodian
    template_name = "custodians/custodian_list.html"
    context_object_name = "custodians"
    paginate_by = 20

@login_required
def custodian_dashboard(request):
    """
    Custodian dashboard view showing all assets assigned to the logged-in custodian
    """
    try:
        # Get the custodian object for the current user
        custodian = get_object_or_404(Custodian, user=request.user, is_active=True)
    except Custodian.DoesNotExist:
        # Handle case where user is not a custodian
        return render(request, 'assets/not_custodian.html')
    
    # Get all assets assigned to this custodian
    assets = Asset.objects.filter(custodian=custodian).select_related(
        'category', 'location', 'location__department'
    ).order_by('-created_at')
    
    # Calculate statistics
    total_assets = assets.count()
    active_assets = assets.filter(status='active').count()
    maintenance_assets = assets.filter(status='maintenance').count()
    retired_assets = assets.filter(status='retired').count()
    
    # Filter assets based on search parameters (for AJAX requests)
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    if search_query:
        assets = assets.filter(
            Q(name__icontains=search_query) |
            Q(asset_code__icontains=search_query) |
            Q(serial_number__icontains=search_query)
        )
    
    if status_filter:
        assets = assets.filter(status=status_filter)
    
    # If this is an AJAX request, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        assets_data = []
        for asset in assets:
            assets_data.append({
                'id': asset.id,
                'name': asset.name,
                'asset_code': asset.asset_code,
                'status': asset.status,
                'status_display': asset.get_status_display(),
                'category': asset.category.name if asset.category else 'Not Assigned',
                'location': str(asset.location) if asset.location else 'Not Assigned',
                'acquisition_date': asset.acquisition_date.strftime('%b %d, %Y') if asset.acquisition_date else 'N/A',
                'acquisition_cost': float(asset.acquisition_cost) if asset.acquisition_cost else 0.00,
                'serial_number': asset.serial_number or '',
                'manufacturer': asset.manufacturer or '',
            })
        
        return JsonResponse({
            'assets': assets_data,
            'total_count': total_assets,
            'filtered_count': len(assets_data)
        })
    
    context = {
        'custodian': custodian,
        'assets': assets,
        'total_assets': total_assets,
        'active_assets': active_assets,
        'maintenance_assets': maintenance_assets,
        'retired_assets': retired_assets,
    }
    
    return render(request, 'assets/custodian_dashboard.html', context)

@login_required
def asset_detail(request, asset_id):
    """
    Asset detail view for custodians
    """
    try:
        custodian = get_object_or_404(Custodian, user=request.user, is_active=True)
    except Custodian.DoesNotExist:
        return render(request, 'assets/not_custodian.html')
    
    # Ensure the asset belongs to this custodian
    asset = get_object_or_404(Asset, id=asset_id, custodian=custodian)
    
    context = {
        'asset': asset,
        'custodian': custodian,
    }
    
    return render(request, 'assets/asset_detail.html', context)

@login_required
def custodian_profile(request):
    """
    Custodian profile view
    """
    try:
        custodian = get_object_or_404(Custodian, user=request.user, is_active=True)
    except Custodian.DoesNotExist:
        return render(request, 'assets/not_custodian.html')
    
    # Get recent activity
    recent_assets = Asset.objects.filter(custodian=custodian).order_by('-updated_at')[:5]
    
    context = {
        'custodian': custodian,
        'recent_assets': recent_assets,
    }