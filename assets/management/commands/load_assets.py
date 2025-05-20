import random
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from assets.models import (Asset, Category, Custodian, Department, Location,
                           MaintenanceRecord, Tag, Vendor)

User = get_user_model()


class Command(BaseCommand):
    help = "Loads initial asset data into the database (30+ items)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting to load asset data..."))

        # Create superuser if not exists
        if not User.objects.filter(email="admin@example.com").exists():
            User.objects.create_superuser(
                email="admin@example.com",
                password="admin123",
                first_name="Admin",
                last_name="User",
            )
            self.stdout.write(self.style.SUCCESS("Created admin user"))

        # Departments
        departments = [
            {"name": "IT", "code": "IT"},
            {"name": "Finance", "code": "FIN"},
            {"name": "Operations", "code": "OPS"},
            {"name": "Human Resources", "code": "HR"},
            {"name": "Marketing", "code": "MKT"},
            {"name": "Research & Development", "code": "RND"},
        ]
        for dept_data in departments:
            Department.objects.get_or_create(**dept_data)
        self.stdout.write(self.style.SUCCESS(f"Created {len(departments)} departments"))

        # Locations
        locations = [
            {
                "name": "HQ Main Office",
                "building": "Main",
                "room": "101",
                "department": "IT",
            },
            {
                "name": "Finance Dept",
                "building": "Main",
                "room": "201",
                "department": "Finance",
            },
            {
                "name": "Server Room",
                "building": "Annex",
                "room": "B1",
                "department": "IT",
            },
            {
                "name": "Marketing Suite",
                "building": "West",
                "room": "301",
                "department": "Marketing",
            },
            {
                "name": "R&D Lab",
                "building": "East",
                "room": "401",
                "department": "Research & Development",
            },
            {
                "name": "Conference Room A",
                "building": "Main",
                "room": "102",
                "department": "Operations",
            },
            {
                "name": "Break Room",
                "building": "Main",
                "room": "103",
                "department": "Human Resources",
            },
        ]
        for loc_data in locations:
            Location.objects.get_or_create(
                name=loc_data["name"],
                building=loc_data["building"],
                room=loc_data["room"],
                defaults={
                    "department": Department.objects.get(name=loc_data["department"])
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Created {len(locations)} locations"))

        # Users and Custodians
        custodian_users = [
            {
                "email": "jdoe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "department": "IT",
            },
            {
                "email": "asmith@example.com",
                "first_name": "Alice",
                "last_name": "Smith",
                "department": "Finance",
            },
            {
                "email": "rjones@example.com",
                "first_name": "Robert",
                "last_name": "Jones",
                "department": "Marketing",
            },
            {
                "email": "lchen@example.com",
                "first_name": "Lisa",
                "last_name": "Chen",
                "department": "Research & Development",
            },
            {
                "email": "mbrown@example.com",
                "first_name": "Michael",
                "last_name": "Brown",
                "department": "Operations",
            },
            {
                "email": "jsmith@example.com",
                "first_name": "Jane",
                "last_name": "Smith",
                "department": "Human Resources",
            },
        ]

        for user_data in custodian_users:
            user, created = User.objects.get_or_create(
                email=user_data["email"],
                defaults={
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                    "password": "password123",
                },
            )
            if created:
                Custodian.objects.create(
                    user=user,
                    department=Department.objects.get(name=user_data["department"]),
                )
        self.stdout.write(
            self.style.SUCCESS(f"Created {len(custodian_users)} custodians")
        )

        # Vendors
        vendors = [
            {
                "name": "Tech Solutions Inc.",
                "email": "sales@techsolutions.com",
                "phone": "555-0101",
            },
            {
                "name": "Office Supplies Co.",
                "email": "contact@officesupplies.com",
                "phone": "555-0202",
            },
            {
                "name": "Equipment Rentals LLC",
                "email": "info@equipmentrentals.com",
                "phone": "555-0303",
            },
            {
                "name": "Furniture World",
                "email": "orders@furnitureworld.com",
                "phone": "555-0404",
            },
            {
                "name": "Network Systems Corp",
                "email": "support@networksystems.com",
                "phone": "555-0505",
            },
        ]
        for vendor_data in vendors:
            Vendor.objects.get_or_create(
                name=vendor_data["name"],
                defaults={"email": vendor_data["email"], "phone": vendor_data["phone"]},
            )
        self.stdout.write(self.style.SUCCESS(f"Created {len(vendors)} vendors"))

        # Categories
        categories = [
            {"name": "Computers", "description": "Desktop and laptop computers"},
            {"name": "Printers", "description": "All types of printers"},
            {"name": "Furniture", "description": "Office furniture and equipment"},
            {"name": "Networking", "description": "Network equipment and devices"},
            {"name": "Electronics", "description": "Miscellaneous electronic devices"},
            {"name": "Lab Equipment", "description": "Specialized research equipment"},
        ]
        for cat_data in categories:
            Category.objects.get_or_create(**cat_data)
        self.stdout.write(self.style.SUCCESS(f"Created {len(categories)} categories"))

        # Tags
        tags = [
            {"name": "High Value", "color": "#FF0000"},
            {"name": "Warranty", "color": "#00FF00"},
            {"name": "Leased", "color": "#0000FF"},
            {"name": "Critical", "color": "#FFFF00"},
            {"name": "Portable", "color": "#FF00FF"},
            {"name": "IT Equipment", "color": "#00FFFF"},
        ]
        for tag_data in tags:
            Tag.objects.get_or_create(**tag_data)
        self.stdout.write(self.style.SUCCESS(f"Created {len(tags)} tags"))

        # Asset Types (for generating varied assets)
        asset_types = [
            {
                "name": "Dell Laptop",
                "manufacturer": "Dell",
                "category": "Computers",
                "price_range": (800, 2500),
                "life_years": (3, 5),
                "depreciation": (20, 30),
            },
            {
                "name": "HP Printer",
                "manufacturer": "HP",
                "category": "Printers",
                "price_range": (300, 1500),
                "life_years": (4, 7),
                "depreciation": (15, 25),
            },
            {
                "name": "Office Chair",
                "manufacturer": "Steelcase",
                "category": "Furniture",
                "price_range": (200, 800),
                "life_years": (5, 10),
                "depreciation": (10, 15),
            },
            {
                "name": "Network Switch",
                "manufacturer": "Cisco",
                "category": "Networking",
                "price_range": (500, 3000),
                "life_years": (5, 8),
                "depreciation": (15, 20),
            },
            {
                "name": "Microscope",
                "manufacturer": "Olympus",
                "category": "Lab Equipment",
                "price_range": (1500, 5000),
                "life_years": (7, 12),
                "depreciation": (8, 12),
            },
            {
                "name": "Projector",
                "manufacturer": "Epson",
                "category": "Electronics",
                "price_range": (600, 2000),
                "life_years": (4, 6),
                "depreciation": (20, 25),
            },
        ]

        # Create a department to custodian mapping
        department_custodians = {}
        for custodian in Custodian.objects.all():
            dept_id = custodian.department.id
            if dept_id not in department_custodians:
                department_custodians[dept_id] = []
            department_custodians[dept_id].append(custodian)

        # Generate 30 assets
        assets_created = 0
        for i in range(1, 31):
            asset_type = random.choice(asset_types)
            model_num = (
                f"{asset_type['manufacturer'][:3].upper()}-{random.randint(1000, 9999)}"
            )
            serial_num = f"{asset_type['manufacturer'][:3].upper()}{random.randint(100000, 999999)}"

            # Randomize values within ranges
            purchase_price = Decimal(random.randint(*asset_type["price_range"]))
            life_years = random.randint(*asset_type["life_years"])
            depreciation = Decimal(random.randint(*asset_type["depreciation"]))

            # Calculate dates
            purchase_date = date.today() - timedelta(days=random.randint(30, 365 * 3))
            warranty_date = purchase_date + timedelta(days=365 * random.randint(1, 3))

            # Random status (mostly active)
            status = (
                "active"
                if random.random() > 0.1
                else random.choice(["inactive", "maintenance", "disposed"])
            )

            # Random location and custodian
            location = random.choice(Location.objects.all())

            # Find custodians for this department or use any custodian if none exists
            dept_id = location.department.id
            if dept_id in department_custodians and department_custodians[dept_id]:
                custodian = random.choice(department_custodians[dept_id])
            else:
                # Fallback to any custodian if none for this department
                custodian = random.choice(Custodian.objects.all())

            asset = Asset.objects.create(
                asset_id=f"AST-{i:04d}",
                name=f"{asset_type['name']} {model_num}",
                description=f"{asset_type['manufacturer']} {asset_type['name']} ({model_num})",
                category=Category.objects.get(name=asset_type["category"]),
                status=status,
                serial_number=serial_num,
                model_number=model_num,
                manufacturer=asset_type["manufacturer"],
                purchase_price=purchase_price,
                purchase_date=purchase_date,
                warranty_expiry_date=warranty_date,
                expected_life_years=life_years,
                depreciation_rate=depreciation,
                vendor=random.choice(Vendor.objects.all()),
                location=location,
                custodian=custodian,
            )

            # Add random tags (1-3 per asset)
            for _ in range(random.randint(1, 3)):
                asset.tags.add(random.choice(Tag.objects.all()))

            assets_created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {assets_created} assets"))

        # Create maintenance records (about 30% of assets)
        assets = Asset.objects.all()
        maintenance_created = 0

        for asset in assets:
            if random.random() <= 0.3:  # 30% chance
                maintenance_types = ["preventive", "corrective", "upgrade"]
                maintenance_type = random.choice(maintenance_types)

                schedule_date = asset.purchase_date + timedelta(
                    days=random.randint(30, 365)
                )
                completion_date = schedule_date + timedelta(days=random.randint(1, 14))

                MaintenanceRecord.objects.create(
                    asset=asset,
                    maintenance_type=maintenance_type,
                    status="completed",
                    schedule_date=schedule_date,
                    completion_date=completion_date,
                    cost=Decimal(random.randint(50, 500)),
                    description=f"{maintenance_type.capitalize()} maintenance for {asset.name}",
                    findings=random.choice(
                        [
                            "Everything working normally",
                            "Replaced worn parts",
                            "Adjusted calibration",
                            "Updated firmware",
                            "Cleaned components",
                        ]
                    ),
                    actions_taken=random.choice(
                        [
                            "Performed routine maintenance",
                            "Replaced defective parts",
                            "Upgraded components",
                            "Adjusted settings",
                            "Cleaned and lubricated",
                        ]
                    ),
                    service_provider=random.choice(Vendor.objects.all()),
                )
                maintenance_created += 1

        self.stdout.write(
            self.style.SUCCESS(f"Created {maintenance_created} maintenance records")
        )
        self.stdout.write(self.style.SUCCESS("Successfully loaded all asset data!"))
