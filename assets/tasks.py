from io import BytesIO

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from reports.services import ReportGenerator


@shared_task
def send_daily_asset_report():
    """Send daily asset report to administrators"""
    from .models import Asset

    assets = Asset.objects.filter(status="active")
    pdf_buffer = ReportGenerator.generate_asset_pdf(assets, "Daily Asset Report")

    email = EmailMessage(
        subject="Daily Asset Report",
        body="Please find attached the daily asset report.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[admin[1] for admin in settings.ADMINS],
    )

    email.attach("daily_asset_report.pdf", pdf_buffer.getvalue(), "application/pdf")
    email.send()
