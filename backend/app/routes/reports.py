
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
