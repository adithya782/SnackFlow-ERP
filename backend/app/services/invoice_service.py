
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4

from app import db
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.sales_order import SalesOrder
from app.models.sales_order_item import SalesOrderItem
from app.models.customer import Customer
from app.models.item import Item
from app.models.company_settings import CompanySettings


CENT = Decimal("0.01")


def money(value):
    return Decimal(str(value)).quantize(
        CENT, rounding=ROUND_HALF_UP
    )


def create_invoice(sales_order_id, user_id):
    # 1. Fetch and validate sales order
    order = db.session.get(SalesOrder, sales_order_id)

    if not order:
        raise ValueError("Sales order not found.")

    if order.status != "APPROVED":
        raise ValueError("Only approved sales orders can be invoiced.")

    # 2. Prevent duplicate invoices
    existing = Invoice.query.filter_by(
        sales_order_id=sales_order_id
    ).first()

    if existing:
        raise ValueError("An invoice already exists for this sales order.")

    # 3. Fetch company and customer details
    company = CompanySettings.query.first()

    if not company:
        raise ValueError("Company settings are not configured.")

    customer = db.session.get(Customer, order.customer_id)

    if not customer:
        raise ValueError("Customer not found.")

    if not company.state or not customer.state:
        raise ValueError("Seller and customer states are required.")

    # 4. Determine GST treatment
    same_state = (
        company.state.strip().casefold()
        == customer.state.strip().casefold()
    )

    # 5. Fetch sales order items
    order_items = SalesOrderItem.query.filter_by(
        sales_order_id=order.id
    ).all()

    if not order_items:
        raise ValueError("Sales order has no items.")

    # 6. Create invoice
    invoice = Invoice(
        invoice_number=f"INV-{date.today():%Y%m%d}-{uuid4().hex[:6].upper()}",
        sales_order_id=order.id,
        customer_id=order.customer_id,
        invoice_date=date.today(),
        status="DRAFT",
        notes=order.notes,
        created_by=user_id
    )

    db.session.add(invoice)
    db.session.flush()

    total_taxable = Decimal("0.00")
    total_cgst = Decimal("0.00")
    total_sgst = Decimal("0.00")
    total_igst = Decimal("0.00")

    # 7. Create invoice line items and calculate GST
    for order_item in order_items:
        item = db.session.get(Item, order_item.item_id)

        if not item:
            raise ValueError("An item in the sales order no longer exists.")

        taxable = money(
            Decimal(str(order_item.quantity))
            * Decimal(str(order_item.unit_price))
            - Decimal(str(order_item.discount_amount or 0))
        )

        tax = money(order_item.tax_amount)

        if taxable < 0 or tax < 0:
            raise ValueError("Invalid sales order amounts.")

        cgst = Decimal("0.00")
        sgst = Decimal("0.00")
        igst = Decimal("0.00")

        if same_state:
            cgst = money(tax / 2)
            sgst = tax - cgst
        else:
            igst = tax

        line_total = taxable + tax

        invoice_item = InvoiceItem(
            invoice_id=invoice.id,
            item_id=item.id,
            description=item.name,
            hsn_code=None,
            quantity=order_item.quantity,
            unit_price=order_item.unit_price,
            discount_amount=order_item.discount_amount,
            taxable_amount=taxable,
            gst_rate=order_item.tax_rate,
            cgst_amount=cgst,
            sgst_amount=sgst,
            igst_amount=igst,
            line_total=line_total
        )

        db.session.add(invoice_item)

        total_taxable += taxable
        total_cgst += cgst
        total_sgst += sgst
        total_igst += igst

    # 8. Update invoice totals
    invoice.taxable_amount = money(total_taxable)
    invoice.cgst_amount = money(total_cgst)
    invoice.sgst_amount = money(total_sgst)
    invoice.igst_amount = money(total_igst)

    invoice.total_tax = money(
        total_cgst + total_sgst + total_igst
    )

    invoice.total_amount = money(
        total_taxable + invoice.total_tax
    )

    db.session.flush()

    return invoice
