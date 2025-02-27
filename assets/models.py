from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Custodian(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.department})"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

class Asset(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    warranty_expiry_date = models.DateField(blank=True, null=True)
    availability = models.BooleanField(default=True)
    custodian = models.ForeignKey(Custodian, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name