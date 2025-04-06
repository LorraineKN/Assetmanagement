# # views.py
# from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.urls import reverse_lazy
# from django.shortcuts import get_object_or_404, redirect
# from django.http import HttpResponse
# from django.db.models import Count, Sum
# import csv
# from datetime import datetime

# from .models import Asset, Category, Department, AssetTransfer

# class DashboardView(LoginRequiredMixin, TemplateView):
#     """Dashboard view showing asset statistics and recent activities"""
#     template_name = 'dashboard.html'
#     login_url = '/login/'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)

#         # Get asset statistics
#         context['total_assets'] = Asset.objects.count()
#         context['active_assets'] = Asset.objects.filter(status='active').count()
#         context['inactive_assets'] = Asset.objects.filter(status='inactive').count()
#         context['maintenance_assets'] = Asset.objects.filter(status='maintenance').count()

#         # Get asset value statistics
#         context['total_asset_value'] = Asset.objects.filter(purchase_price__isnull=False).aggregate(
#             Sum('purchase_price'))['purchase_price__sum'] or 0

#         # Get category distribution
#         categories = Category.objects.annotate(asset_count=Count('asset'))
#         context['categories'] = categories

#         # Recent activities
#         context['recent_transfers'] = AssetTransfer.objects.order_by('-transfer_date')[:5]
#         context['recent_maintenance'] = AssetMaintenance.objects.order_by('-maintenance_date')[:5]

#         # Recently added assets
#         context['recent_assets'] = Asset.objects.order_by('-created_at')[:6]

#         return context

# class AssetListView(LoginRequiredMixin, ListView):
#     """List view for assets with filtering capabilities"""
#     model = Asset
#     template_name = 'list.html'
#     context_object_name = 'assets'
#     paginate_by = 12
#     login_url = '/login/'

#     def get_queryset(self):
#         queryset = Asset.objects.all()

#         # Apply filters from GET parameters
#         search = self.request.GET.get('search', '')
#         status = self.request.GET.get('status', '')
#         category_id = self.request.GET.get('category', '')
#         department_id = self.request.GET.get('department', '')

#         if search:
#             queryset = queryset.filter(
#                 Q(name__icontains=search) |
#                 Q(asset_id__icontains=search) |
#                 Q(description__icontains=search)
#             )

#         if status:
#             queryset = queryset.filter(status=status)

#         if category_id and category_id.isdigit():
#             queryset = queryset.filter(category_id=int(category_id))

#         if department_id and department_id.isdigit():
#             queryset = queryset.filter(department_id=int(department_id))

#         return queryset.order_by('-created_at')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['status_choices'] = Asset.STATUS_CHOICES
#         context['categories'] = Category.objects.all()
#         context['departments'] = Department.objects.all()
#         return context

# class AssetDetailView(LoginRequiredMixin, DetailView):
#     """Detailed view of a single asset"""
#     model = Asset
#     template_name = 'asset_detail.html'
#     context_object_name = 'asset'
#     login_url = '/login/'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         asset = self.get_object()
#         context['maintenance_history'] = AssetMaintenance.objects.filter(asset=asset).order_by('-maintenance_date')
#         context['transfer_history'] = AssetTransfer.objects.filter(asset=asset).order_by('-transfer_date')
#         return context

# class AssetCreateView(LoginRequiredMixin, CreateView):
#     """Create a new asset"""
#     model = Asset
#     form_class = AssetForm
#     template_name = 'asset_form.html'
#     success_url = reverse_lazy('asset_list')
#     login_url = '/login/'

#     def form_valid(self, form):
#         form.instance.created_by = self.request.user
#         return super().form_valid(form)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = 'Add New Asset'
#         return context

# class AssetUpdateView(LoginRequiredMixin, UpdateView):
#     """Update an existing asset"""
#     model = Asset
#     form_class = AssetForm
#     template_name = 'asset_form.html'
#     login_url = '/login/'

#     def get_success_url(self):
#         return reverse_lazy('asset_detail', kwargs={'pk': self.object.pk})

#     def form_valid(self, form):
#         form.instance.updated_by = self.request.user
#         return super().form_valid(form)

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = 'Update Asset'
#         return context

# class AssetDeleteView(LoginRequiredMixin, DeleteView):
#     """Delete an asset"""
#     model = Asset
#     success_url = reverse_lazy('asset_list')
#     login_url = '/login/'

#     def post(self, request, *args, **kwargs):
#         # Add logic here if needed before deletion
#         return super().post(request, *args, **kwargs)

# class AssetTransferView(LoginRequiredMixin, CreateView):
#     """Transfer an asset to another custodian/location"""
#     model = AssetTransfer
#     form_class = AssetTransferForm
#     template_name = 'asset_transfer_form.html'
#     login_url = '/login/'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         asset_id = self.kwargs.get('pk')
#         asset = get_object_or_404(Asset, pk=asset_id)
#         context['asset'] = asset
#         context['title'] = f'Transfer Asset: {asset.name}'
#         return context

#     def form_valid(self, form):
#         asset_id = self.kwargs.get('pk')
#         asset = get_object_or_404(Asset, pk=asset_id)
#         form.instance.asset = asset
#         form.instance.transferred_by = self.request.user

#         # Update the asset's custodian and location
#         asset.custodian = form.cleaned_data['new_custodian']
#         asset.location = form.cleaned_data['new_location']
#         asset.save()

#         return super().form_valid(form)

#     def get_success_url(self):
#         return reverse_lazy('asset_detail', kwargs={'pk': self.kwargs.get('pk')})

# class AssetMaintenanceView(LoginRequiredMixin, CreateView):
#     """Record maintenance for an asset"""
#     model = AssetMaintenance
#     form_class = AssetMaintenanceForm
#     template_name = 'asset_maintenance_form.html'
#     login_url = '/login/'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         asset_id = self.kwargs.get('pk')
#         asset = get_object_or_404(Asset, pk=asset_id)
#         context['asset'] = asset
#         context['title'] = f'Record Maintenance: {asset.name}'
#         return context

#     def form_valid(self, form):
#         asset_id = self.kwargs.get('pk')
#         asset = get_object_or_404(Asset, pk=asset_id)
#         form.instance.asset = asset
#         form.instance.performed_by = self.request.user

#         # If maintenance changes status, update the asset
#         if form.cleaned_data.get('update_status', False):
#             asset.status = form.cleaned_data.get('new_status', asset.status)
#             asset.save()

#         return super().form_valid(form)

#     def get_success_url(self):
#         return reverse_lazy('asset_detail', kwargs={'pk': self.kwargs.get('pk')})

# def asset_export(request):
#     """Export assets to CSV file"""
#     if not request.user.is_authenticated:
#         return redirect('login')

#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = f'attachment; filename="assets_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'

#     writer = csv.writer(response)
#     writer.writerow(['Asset ID', 'Name', 'Category', 'Status', 'Location',
#                      'Custodian', 'Purchase Date', 'Purchase Price', 'Warranty Expiry'])

#     # Apply filters if any
#     assets = Asset.objects.all()
#     search = request.GET.get('search', '')
#     status = request.GET.get('status', '')
#     category_id = request.GET.get('category', '')
#     department_id = request.GET.get('department', '')

#     if search:
#         assets = assets.filter(
#             Q(name__icontains=search) |
#             Q(asset_id__icontains=search) |
#             Q(description__icontains=search)
#         )

#     if status:
#         assets = assets.filter(status=status)

#     if category_id and category_id.isdigit():
#         assets = assets.filter(category_id=int(category_id))

#     if department_id and department_id.isdigit():
#         assets = assets.filter(department_id=int(department_id))

#     for asset in assets:
#         writer.writerow([
#             asset.asset_id,
#             asset.name,
#             asset.category.name if asset.category else 'Uncategorized',
#             asset.get_status_display(),
#             asset.location,
#             asset.custodian.user.get_full_name() if asset.custodian else 'Unassigned',
#             asset.purchase_date.strftime('%Y-%m-%d') if asset.purchase_date else '',
#             asset.purchase_price,
#             asset.warranty_end_date.strftime('%Y-%m-%d') if asset.warranty_end_date else ''
#         ])

#     return response
