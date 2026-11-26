
import csv
from io import BytesIO, StringIO

from flask import Blueprint, jsonify, send_file, make_response
from flask_jwt_extended import jwt_required
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from app.services.report_service import (
    get_inventory_report,
    get_sales_report,
    get_production_report,
    get_receivables_report
)
from app.models.customer import Customer
from app.utils.decorators import role_required
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

reports_bp = Blueprint(
    "reports",
    __name__,
    url_prefix="/api/reports"
)


def create_excel_file(headers, rows, sheet_name):
    """Generate an Excel workbook in memory."""

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = sheet_name

    worksheet.append(headers)

    for cell in worksheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(
            start_color="176B45",
            end_color="176B45",
            fill_type="solid"
        )
        cell.alignment = Alignment(horizontal="center")

    for row in rows:
        worksheet.append(row)

    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions

    for column in worksheet.columns:
        max_length = max(
            len(str(cell.value or "")) for cell in column
        )
        worksheet.column_dimensions[
            column[0].column_letter
        ].width = min(max_length + 3, 35)

    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    return output


def create_csv_file(headers, rows):
    """Generate a CSV file in memory."""

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(headers)
    writer.writerows(rows)

    response = make_response(
        "\ufeff" + output.getvalue()
    )
    response.headers["Content-Type"] = "text/csv; charset=utf-8"

    return response


def create_table_pdf(title, summary, headers, rows, column_widths=None):
    """Generate a formatted PDF report with a summary and data table."""

    output = BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=landscape(A4),
        rightMargin=25,
        leftMargin=25,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(title, styles["Title"]))
    elements.append(Spacer(1, 15))

    if summary:
        summary_data = [list(summary.keys()), list(summary.values())]

        summary_table = Table(summary_data, repeatRows=1)
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#176B45")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 8),
        ]))

        elements.append(summary_table)
        elements.append(Spacer(1, 20))

    table_data = [headers] + [
        [str(value if value is not None else "-") for value in row]
        for row in rows
    ]

    report_table = Table(
        table_data,
        repeatRows=1,
        colWidths=column_widths
    )

    report_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#176B45")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#F2F6F3")
        ]),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))

    elements.append(report_table)

    document.build(elements)

    output.seek(0)
    return output


def create_production_pdf(production):
    """Generate a formatted production report PDF in memory."""

    output = BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=landscape(A4),
        rightMargin=25,
        leftMargin=25,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(
        Paragraph("SnackFlow - Production Report", styles["Title"])
    )
    elements.append(Spacer(1, 15))

    runs = production.get("production_runs", [])

    summary_data = [
        ["Total Production Runs", "Completed Runs"],
        [
            production.get("total_runs", len(runs)),
            production.get(
                "completed_runs",
                sum(1 for run in runs if run["status"] == "COMPLETED")
            )
        ]
    ]

    summary_table = Table(summary_data, colWidths=[180, 180])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#176B45")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    headers = [
        "Run Number",
        "Date",
        "Planned",
        "Actual",
        "Material",
        "Labour",
        "Gas/Power",
        "Other",
        "Total Cost",
        "Cost/Unit",
        "Status"
    ]

    table_data = [headers]

    for run in runs:
        table_data.append([
            str(run.get("run_number", "")),
            str(run.get("production_date", "")),
            str(run.get("planned_output", "")),
            str(run.get("actual_output") or "-"),
            f'Rs. {float(run.get("material_cost") or 0):.2f}',
            f'Rs. {float(run.get("labour_cost") or 0):.2f}',
            f'Rs. {float(run.get("gas_power_cost") or 0):.2f}',
            f'Rs. {float(run.get("other_overhead") or 0):.2f}',
            f'Rs. {float(run.get("total_production_cost") or 0):.2f}',
            f'Rs. {float(run.get("cost_per_unit") or 0):.2f}',
            str(run.get("status", ""))
        ])

    production_table = Table(
        table_data,
        repeatRows=1,
        colWidths=[95, 65, 48, 45, 65, 55, 65, 55, 70, 65, 55]
    )

    production_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#176B45")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#F2F6F3")
        ]),
        ("PADDING", (0, 0), (-1, -1), 5),
    ]))

    elements.append(production_table)

    document.build(elements)

    output.seek(0)
    return output


def export_report(headers, rows, filename, sheet_name, file_format):
    """Return an Excel or CSV download."""

    if file_format == "csv":
        response = create_csv_file(headers, rows)
        response.headers["Content-Disposition"] = (
            f'attachment; filename="{filename}.csv"'
        )
        return response

    if file_format == "xlsx":
        output = create_excel_file(headers, rows, sheet_name)

        return send_file(
            output,
            as_attachment=True,
            download_name=f"{filename}.xlsx",
            mimetype=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )

    return jsonify({
        "message": "Unsupported format. Use csv or xlsx."
    }), 400


@reports_bp.route("/inventory", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT", "PRODUCTION")
def inventory_report():
    return jsonify(get_inventory_report()), 200


@reports_bp.route("/sales", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT")
def sales_report():
    return jsonify(get_sales_report()), 200


@reports_bp.route("/production", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT", "PRODUCTION")
def production_report():
    return jsonify(get_production_report()), 200


@reports_bp.route("/receivables", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT")
def receivables_report():
    return jsonify(get_receivables_report()), 200


@reports_bp.route("/inventory/export/<file_format>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT", "PRODUCTION")
def export_inventory_report(file_format):

    inventory = get_inventory_report()

    headers = [
        "Item ID",
        "Item Name",
        "SKU",
        "Category",
        "Unit",
        "Current Stock",
        "Reorder Level",
        "Stock Status"
    ]

    rows = [
        [
            item["item_id"],
            item["name"],
            item["sku"],
            item["category"],
            item["unit"],
            item["current_stock"],
            item["reorder_level"],
            "Low Stock" if item["low_stock"] else "Healthy"
        ]
        for item in inventory
    ]

    return export_report(
        headers,
        rows,
        "SnackFlow_Stock_Report",
        "Stock Report",
        file_format.lower()
    )


@reports_bp.route("/sales/export/<file_format>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT")
def export_sales_report(file_format):

    sales = get_sales_report()

    customer_ids = {
        invoice["customer_id"]
        for invoice in sales["invoices"]
    }

    customers = Customer.query.filter(
        Customer.id.in_(customer_ids)
    ).all() if customer_ids else []

    customer_map = {
        customer.id: customer.business_name
        for customer in customers
    }

    headers = [
        "Invoice ID",
        "Invoice Number",
        "Customer",
        "Invoice Date",
        "Total Amount",
        "Status"
    ]

    rows = [
        [
            invoice["invoice_id"],
            invoice["invoice_number"],
            customer_map.get(invoice["customer_id"], "Unknown"),
            invoice["invoice_date"],
            invoice["total_amount"],
            invoice["status"]
        ]
        for invoice in sales["invoices"]
    ]

    return export_report(
        headers,
        rows,
        "SnackFlow_Sales_Register",
        "Sales Register",
        file_format.lower()
    )


@reports_bp.route("/production/export/<file_format>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT", "PRODUCTION")
def export_production_report(file_format):

    production = get_production_report()

    headers = [
        "Run Number",
        "Production Date",
        "Planned Output",
        "Actual Output",
        "Material Cost",
        "Labour Cost",
        "Gas / Power Cost",
        "Other Overheads",
        "Total Overhead",
        "Total Production Cost",
        "Cost Per Unit",
        "Status"
    ]

    rows = [
        [
            run["run_number"],
            run["production_date"],
            run["planned_output"],
            run["actual_output"],
            run["material_cost"],
            run["labour_cost"],
            run["gas_power_cost"],
            run["other_overhead"],
            run["total_overhead"],
            run["total_production_cost"],
            run["cost_per_unit"],
            run["status"]
        ]
        for run in production["production_runs"]
    ]

    return export_report(
        headers,
        rows,
        "SnackFlow_Production_Report",
        "Production Report",
        file_format.lower()
    )


@reports_bp.route("/production/export/pdf", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT", "PRODUCTION")
def export_production_pdf():

    production = get_production_report()
    output = create_production_pdf(production)

    return send_file(
        output,
        as_attachment=True,
        download_name="SnackFlow_Production_Report.pdf",
        mimetype="application/pdf"
    )


@reports_bp.route("/inventory/export/pdf", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT", "PRODUCTION")
def export_inventory_pdf():

    inventory = get_inventory_report()

    headers = [
        "Item Name",
        "SKU",
        "Category",
        "Unit",
        "Current Stock",
        "Reorder Level",
        "Stock Status"
    ]

    rows = [
        [
            item["name"],
            item["sku"],
            item["category"],
            item["unit"],
            item["current_stock"],
            item["reorder_level"],
            "Low Stock" if item["low_stock"] else "Healthy"
        ]
        for item in inventory
    ]

    low_stock_count = sum(
        1 for item in inventory if item["low_stock"]
    )

    output = create_table_pdf(
        title="SnackFlow - Inventory Report",
        summary={
            "Total Items": len(inventory),
            "Low Stock Items": low_stock_count,
            "Healthy Items": len(inventory) - low_stock_count
        },
        headers=headers,
        rows=rows,
        column_widths=[125, 85, 95, 65, 85, 85, 90]
    )

    return send_file(
        output,
        as_attachment=True,
        download_name="SnackFlow_Stock_Report.pdf",
        mimetype="application/pdf"
    )


@reports_bp.route("/sales/export/pdf", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT")
def export_sales_pdf():

    sales = get_sales_report()

    customer_ids = {
        invoice["customer_id"]
        for invoice in sales["invoices"]
    }

    customers = Customer.query.filter(
        Customer.id.in_(customer_ids)
    ).all() if customer_ids else []

    customer_map = {
        customer.id: customer.business_name
        for customer in customers
    }

    headers = [
        "Invoice Number",
        "Customer",
        "Invoice Date",
        "Total Amount",
        "Status"
    ]

    rows = [
        [
            invoice["invoice_number"],
            customer_map.get(invoice["customer_id"], "Unknown"),
            invoice["invoice_date"],
            f'Rs. {float(invoice["total_amount"] or 0):.2f}',
            invoice["status"]
        ]
        for invoice in sales["invoices"]
    ]

    output = create_table_pdf(
        title="SnackFlow - Sales Report",
        summary={
            "Total Sales": f'Rs. {float(sales["total_sales"] or 0):.2f}',
            "Total Tax": f'Rs. {float(sales["total_tax"] or 0):.2f}',
            "Invoices Issued": sales["total_invoices"]
        },
        headers=headers,
        rows=rows,
        column_widths=[125, 145, 100, 110, 90]
    )

    return send_file(
        output,
        as_attachment=True,
        download_name="SnackFlow_Sales_Register.pdf",
        mimetype="application/pdf"
    )
