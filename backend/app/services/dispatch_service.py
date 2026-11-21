
from datetime import date
from uuid import uuid4

from app import db
from app.models.dispatch import Dispatch
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.services.inventory_service import record_stock_movement


def create_dispatch(data, user_id):
    invoice_id = data.get("invoice_id")

    invoice = db.session.get(Invoice, invoice_id)

    if not invoice:
        raise ValueError("Invoice not found.")

    if invoice.status != "ISSUED":
        raise ValueError("Only issued invoices can be dispatched.")

    existing = Dispatch.query.filter_by(invoice_id=invoice_id).first()

    if existing:
        raise ValueError("A dispatch already exists for this invoice.")

    dispatch = Dispatch(
        dispatch_number=f"DSP-{date.today().strftime('%Y%m%d')}-{uuid4().hex[:6].upper()}",
        invoice_id=invoice_id,
        dispatch_date=date.today(),
        transporter_name=data.get("transporter_name"),
        vehicle_number=data.get("vehicle_number"),
        tracking_number=data.get("tracking_number"),
        notes=data.get("notes"),
        status="PREPARED"
    )

    db.session.add(dispatch)
    db.session.flush()

    return dispatch


def dispatch_goods(dispatch_id, user_id):
    dispatch = db.session.get(Dispatch, dispatch_id)

    if not dispatch:
        raise ValueError("Dispatch not found.")

    if dispatch.status != "PREPARED":
        raise ValueError("Only prepared dispatches can be dispatched.")

    invoice_items = InvoiceItem.query.filter_by(
        invoice_id=dispatch.invoice_id
    ).all()

    if not invoice_items:
        raise ValueError("Invoice has no items.")

    # Deduct finished goods stock.
    for item in invoice_items:
        record_stock_movement(
            item_id=item.item_id,
            movement_type="OUT",
            quantity=item.quantity,
            reference_type="DISPATCH",
            reference_id=dispatch.id,
            created_by=user_id,
            notes=f"Dispatched against {dispatch.dispatch_number}"
        )

    dispatch.status = "DISPATCHED"
    dispatch.dispatched_by = user_id

    return dispatch
