from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone


class NotificationService:
    @staticmethod
    @shared_task
    def send_asset_notification(recipient_emails, subject, template_name, context):
        """Send email notification about asset events"""
        html_content = render_to_string(f"emails/{template_name}", context)
        text_content = render_to_string(f"emails/{template_name}_text", context)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipient_emails,
            reply_to=[settings.REPLY_TO_EMAIL],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    @staticmethod
    def send_maintenance_reminder(asset, maintenance_date):
        """Send maintenance reminder"""
        subject = f"Maintenance Reminder for {asset.name}"
        context = {
            "asset": asset,
            "maintenance_date": maintenance_date,
            "today": timezone.now().date(),
        }

        recipients = []
        if asset.custodian and asset.custodian.user.email:
            recipients.append(asset.custodian.user.email)

        NotificationService.send_asset_notification.delay(
            recipients, subject, "maintenance_reminder", context
        )
