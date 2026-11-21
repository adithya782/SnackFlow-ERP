from flask import send_file
from app.models.customer import Customer
from app.models.company_settings import CompanySettings
from app.utils.invoice_pdf import generate_invoice_pdf
from app.services.audit_service import log_action

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.services.invoice_service import create_invoice
from app.utils.decorators import role_required


invoices_bp = Blueprint(
    "invoices",
    __name__,
    url_prefix="/api/invoices"
)


def serialize_invoice(invoice):
    items = InvoiceItem.query.filter_by(
        invoice_id=invoice.id
    ).all()

    return {
        "id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "sales_order_id": invoice.sales_order_id,
        "customer_id": invoice.customer_id,
        "invoice_date": invoice.invoice_date.isoformat(),
        "taxable_amount": str(invoice.taxable_amount),
        "cgst_amount": str(invoice.cgst_amount),
        "sgst_amount": str(invoice.sgst_amount),
        "igst_amount": str(invoice.igst_amount),
        "total_tax": str(invoice.total_tax),
        "total_amount": str(invoice.total_amount),
        "status": invoice.status,
        "items": [
            {
                "item_id": item.item_id,
                "description": item.description,
                "quantity": str(item.quantity),
                "unit_price": str(item.unit_price),
                "taxable_amount": str(item.taxable_amount),
                "gst_rate": str(item.gst_rate),
                "cgst_amount": str(item.cgst_amount),
                "sgst_amount": str(item.sgst_amount),
                "igst_amount": str(item.igst_amount),
                "line_total": str(item.line_total)
            }
            for item in items
        ]
    }


@invoices_bp.route("", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT")
def get_invoices():
    invoices = Invoice.query.order_by(
        Invoice.id.desc()
    ).all()

    return jsonify({
        "invoices": [
            serialize_invoice(invoice)
            for invoice in invoices
        ]
    }), 200


@invoices_bp.route("/<int:invoice_id>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT")
def get_invoice(invoice_id):
    invoice = db.session.get(Invoice, invoice_id)

    if not invoice:
        return jsonify({"message": "Invoice not found."}), 404

    return jsonify({
        "invoice": serialize_invoice(invoice)
    }), 200


@invoices_bp.route(
    "/from-sales-order/<int:order_id>",
    methods=["POST"]
)
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT")
def generate_invoice(order_id):
    user_id = int(get_jwt_identity())

    try:
        invoice = create_invoice(order_id, user_id)
        db.session.commit()

        return jsonify({
            "message": "Draft invoice created successfully.",
            "invoice": serialize_invoice(invoice)
        }), 201

    except ValueError as error:
        db.session.rollback()
        return jsonify({"message": str(error)}), 400

    except Exception:
        db.session.rollback()
        return jsonify({
            "message": "Unable to create invoice."
        }), 500



@invoices_bp.route("/<int:invoice_id>/pdf", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT")
def download_invoice_pdf(invoice_id):
    invoice = db.session.get(Invoice, invoice_id)

    if not invoice:
        return jsonify({"message": "Invoice not found."}), 404

    company = CompanySettings.query.first()
    customer = db.session.get(Customer, invoice.customer_id)

    if not company or not customer:
        return jsonify({
            "message": "Company or customer details are missing."
        }), 400

    items = InvoiceItem.query.filter_by(
        invoice_id=invoice.id
    ).all()

    pdf_buffer = generate_invoice_pdf(
        invoice,
        company,
        customer,
        items
    )

    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{invoice.invoice_number}.pdf"
    )


@invoices_bp.route("/<int:invoice_id>/issue", methods=["POST"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT")
def issue_invoice(invoice_id):
    invoice = db.session.get(Invoice, invoice_id)

    if not invoice:
        return jsonify({"message": "Invoice not found."}), 404

    if invoice.status != "DRAFT":
        return jsonify({
            "message": "Only draft invoices can be issued."
        }), 400

    try:
        invoice.status = "ISSUED"
        log_action(
            user_id=int(get_jwt_identity()),
            action="ISSUE",
            entity_type="INVOICE",
            entity_id=invoice.id,
            description=f"Invoice {invoice.invoice_number} issued."
        )
        db.session.commit()

        return jsonify({
            "message": "Invoice issued successfully.",
            "invoice": serialize_invoice(invoice)
        }), 200

    except Exception:
        db.session.rollback()
        return jsonify({
            "message": "Unable to issue invoice."
        }), 500
