# reports/services.py
import csv
from io import BytesIO, StringIO

from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle


class ReportGenerator:
    @staticmethod
    def generate_asset_csv(queryset):
        """Generate CSV report for assets"""
        buffer = StringIO()
        writer = csv.writer(buffer)

        # Write header
        writer.writerow(
            [
                "Asset ID",
                "Name",
                "Category",
                "Status",
                "Location",
                "Custodian",
                "Purchase Date",
                "Purchase Price",
                "Current Value",
            ]
        )

        # Write data
        for asset in queryset:
            writer.writerow(
                [
                    asset.asset_id,
                    asset.name,
                    asset.category.name if asset.category else "",
                    asset.get_status_display(),
                    str(asset.location) if asset.location else "",
                    str(asset.custodian) if asset.custodian else "",
                    (
                        asset.purchase_date.strftime("%Y-%m-%d")
                        if asset.purchase_date
                        else ""
                    ),
                    str(asset.purchase_price) if asset.purchase_price else "",
                    str(asset.current_value) if asset.current_value else "",
                ]
            )

        buffer.seek(0)
        return buffer

    @staticmethod
    def generate_asset_pdf(queryset, title="Asset Report"):
        """Generate PDF report for assets"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        styles = getSampleStyleSheet()
        elements.append(Paragraph(title, styles["Title"]))

        # Prepare data
        data = [["Asset ID", "Name", "Status", "Location", "Value"]]

        for asset in queryset:
            data.append(
                [
                    asset.asset_id,
                    asset.name,
                    asset.get_status_display(),
                    str(asset.location) if asset.location else "",
                    f"${asset.current_value:,.2f}" if asset.current_value else "",
                ]
            )

        # Create table
        table = Table(data)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 14),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

        elements.append(table)
        doc.build(elements)
        buffer.seek(0)
        return buffer
