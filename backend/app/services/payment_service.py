
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from uuid import uuid4

from app import db
from app.models.payment import Payment
from app.models.payment_allocation import PaymentAllocation
from app.models.invoice import Invoice
from app.models.customer import Customer


PAYMENT_METHODS = {
    "CASH", "UPI", "BANK_TRANSFER", "CHEQUE", "OTHER"
}


def to_decimal(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("Invalid amount.")


def create_payment(data, user_id):
    customer_id = data.get("customer_id")

    customer = db.session.get(Customer, customer_id)

    if not customer or not customer.is_active:
        raise ValueError("Active customer not found.")

    amount = to_decimal(data.get("amount"))

    if amount <= 0:
        raise ValueError("Payment amount must be positive.")

    method = data.get("payment_method", "").upper()

    if method not in PAYMENT_METHODS:
        raise ValueError("Invalid payment method.")

    payment = Payment(
        payment_number=f"PAY-{date.today().strftime('%Y%m%d')}-{uuid4().hex[:6].upper()}",
        customer_id=customer_id,
        payment_date=date.today(),
        amount=amount.quantize(Decimal("0.01")),
        payment_method=method,
        reference_number=data.get("reference_number"),
        notes=data.get("notes"),
        status="RECEIVED",
        received_by=user_id
    )

    db.session.add(payment)
    db.session.flush()

    return payment


def allocate_payment(payment_id, data):
    payment = db.session.get(Payment, payment_id)

    if not payment:
        raise ValueError("Payment not found.")

    if payment.status != "RECEIVED":
        raise ValueError("Only received payments can be allocated.")

    invoice_id = data.get("invoice_id")
    invoice = db.session.get(Invoice, invoice_id)

    if not invoice:
        raise ValueError("Invoice not found.")

    if invoice.status != "ISSUED":
        raise ValueError("Only issued invoices can receive allocations.")

    if invoice.customer_id != payment.customer_id:
        raise ValueError("Payment and invoice belong to different customers.")

    amount = to_decimal(data.get("allocated_amount"))

    if amount <= 0:
        raise ValueError("Allocation amount must be positive.")

    # Amount already allocated from this payment.
    payment_allocated = db.session.query(
        db.func.coalesce(
            db.func.sum(PaymentAllocation.allocated_amount), 0
        )
    ).filter(
        PaymentAllocation.payment_id == payment.id
    ).scalar()

    payment_available = Decimal(str(payment.amount)) - Decimal(str(payment_allocated))

    if amount > payment_available:
        raise ValueError("Allocation exceeds the available payment amount.")

    # Outstanding amount on this invoice.
    invoice_allocated = db.session.query(
        db.func.coalesce(
            db.func.sum(PaymentAllocation.allocated_amount), 0
        )
    ).join(
        Payment,
        Payment.id == PaymentAllocation.payment_id
    ).filter(
        PaymentAllocation.invoice_id == invoice.id,
        Payment.status == "RECEIVED"
    ).scalar()

    outstanding = Decimal(str(invoice.total_amount)) - Decimal(str(invoice_allocated))

    if amount > outstanding:
        raise ValueError("Allocation exceeds the invoice outstanding amount.")

    existing = PaymentAllocation.query.filter_by(
        payment_id=payment.id,
        invoice_id=invoice.id
    ).first()

    if existing:
        raise ValueError(
            "This payment is already allocated to this invoice."
        )

    allocation = PaymentAllocation(
        payment_id=payment.id,
        invoice_id=invoice.id,
        allocated_amount=amount.quantize(Decimal("0.01"))
    )

    db.session.add(allocation)
    db.session.flush()

    return allocation


def get_invoice_outstanding(invoice_id):
    invoice = db.session.get(Invoice, invoice_id)

    if not invoice:
        raise ValueError("Invoice not found.")

    allocated = db.session.query(
        db.func.coalesce(
            db.func.sum(PaymentAllocation.allocated_amount), 0
        )
    ).join(
        Payment,
        Payment.id == PaymentAllocation.payment_id
    ).filter(
        PaymentAllocation.invoice_id == invoice.id,
        Payment.status == "RECEIVED"
    ).scalar()

    outstanding = Decimal(str(invoice.total_amount)) - Decimal(str(allocated))

    return {
        "invoice_id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "invoice_total": str(invoice.total_amount),
        "paid_amount": str(allocated),
        "outstanding_amount": str(outstanding)
    }
