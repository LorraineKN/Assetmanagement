from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

User = get_user_model()


class BaseModel(models.Model):
    """Abstract base model for common fields"""

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )

    class Meta:
        abstract = True


class Department(BaseModel):
    """Organizational department model"""

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )

    def __str__(self):
        return self.name


class Location(BaseModel):
    """Physical location model for assets"""

    name = models.CharField(max_length=100)
    building = models.CharField(max_length=100, blank=True, null=True)
    room = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("building", "room")

    def __str__(self):
        return (
            f"{self.building} - {self.room}"
            if self.building and self.room
            else self.name
        )


class Custodian(BaseModel):
    """Asset custodian model extending user profile"""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.department})"


class Vendor(BaseModel):
    """Vendor/supplier model"""

    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    tax_id = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Category(BaseModel):
    """Asset category model"""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subcategories",
    )

    def __str__(self):
        return self.name


class Tag(BaseModel):
    """Tag model for asset classification"""

    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default="#007bff")

    def __str__(self):
        return self.name


class Asset(BaseModel):
    """Core asset model"""

    ASSET_STATUS = (
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("lost", "Lost"),
        ("stolen", "Stolen"),
        ("disposed", "Disposed"),
        ("maintenance", "Under Maintenance"),
    )

    asset_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True
    )
    tags = models.ManyToManyField(Tag, blank=True)
    status = models.CharField(max_length=20, choices=ASSET_STATUS, default="active")
    serial_number = models.CharField(max_length=100, blank=True, null=True, unique=True)
    model_number = models.CharField(max_length=100, blank=True, null=True)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    purchase_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    current_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
    )
    purchase_date = models.DateField(blank=True, null=True)
    purchase_order = models.CharField(max_length=100, blank=True, null=True)
    warranty_expiry_date = models.DateField(blank=True, null=True)
    expected_life_years = models.PositiveIntegerField(blank=True, null=True)
    depreciation_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True
    )
    custodian = models.ForeignKey(
        Custodian, on_delete=models.SET_NULL, null=True, blank=True
    )
    image = models.ImageField(upload_to="assets/", blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    last_audited = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.asset_id} - {self.name}"

    def save(self, *args, **kwargs):
        """Calculate current value based on depreciation if not set"""
        if (
            not self.current_value
            and self.purchase_price
            and self.purchase_date
            and self.depreciation_rate
        ):
            years_owned = (timezone.now().date() - self.purchase_date).days / 365.25
            # Convert depreciation_factor to Decimal before multiplication
            depreciation_factor = min(
                Decimal(str(years_owned)) * (self.depreciation_rate / Decimal('100')), 
                Decimal('1')
            )
            self.current_value = max(
                self.purchase_price * (Decimal('1') - depreciation_factor), 
                Decimal('0')
            )
        super().save(*args, **kwargs)


class MaintenanceRecord(BaseModel):
    """Asset maintenance tracking model"""

    MAINTENANCE_TYPES = (
        ("preventive", "Preventive"),
        ("corrective", "Corrective"),
        ("upgrade", "Upgrade"),
    )

    STATUS_CHOICES = (
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name="maintenance_records"
    )
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPES)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="scheduled"
    )
    schedule_date = models.DateField()
    completion_date = models.DateField(blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    service_provider = models.ForeignKey(
        Vendor, on_delete=models.SET_NULL, null=True, blank=True
    )
    description = models.TextField()
    findings = models.TextField(blank=True, null=True)
    actions_taken = models.TextField(blank=True, null=True)
    next_maintenance_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.asset} - {self.get_maintenance_type_display()} on {self.schedule_date}"


class AssetTransfer(BaseModel):
    """Asset transfer/history model"""

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="transfers")
    from_location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="transfers_out"
    )
    to_location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="transfers_in"
    )
    from_custodian = models.ForeignKey(
        Custodian,
        on_delete=models.CASCADE,
        related_name="transfers_out",
        null=True,
        blank=True,
    )
    to_custodian = models.ForeignKey(
        Custodian,
        on_delete=models.CASCADE,
        related_name="transfers_in",
        null=True,
        blank=True,
    )
    transfer_date = models.DateField(default=timezone.now)
    reason = models.TextField(blank=True, null=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_transfers",
    )

    def __str__(self):
        return f"{self.asset} transferred on {self.transfer_date}"


class DepreciationRecord(BaseModel):
    """Asset depreciation history model"""

    asset = models.ForeignKey(
        Asset, on_delete=models.CASCADE, related_name="depreciations"
    )
    record_date = models.DateField(default=timezone.now)
    value_before = models.DecimalField(max_digits=12, decimal_places=2)
    value_after = models.DecimalField(max_digits=12, decimal_places=2)
    depreciation_amount = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.asset} depreciation on {self.record_date}"


class AuditLog(BaseModel):
    """System audit log model"""

    ACTION_CHOICES = (
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("checkout", "Checkout"),
        ("checkin", "Checkin"),
        ("transfer", "Transfer"),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    details = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_action_display()} on {self.model_name} by {self.user}"


class FinancialTransaction(BaseModel):
    """Financial transactions related to assets"""

    TRANSACTION_TYPES = (
        ("purchase", "Purchase"),
        ("maintenance", "Maintenance"),
        ("disposal", "Disposal"),
        ("upgrade", "Upgrade"),
        ("other", "Other"),
    )

    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.TextField()
    asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    document = models.FileField(upload_to="financial_docs/", blank=True, null=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.amount} on {self.date}"
