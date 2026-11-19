from app import db


class PaymentAllocation(db.Model):
    __tablename__ = "payment_allocations"

    id = db.Column(db.Integer, primary_key=True)

    payment_id = db.Column(db.Integer,db.ForeignKey("payments.id"),nullable=False)

    invoice_id = db.Column(db.Integer,db.ForeignKey("invoices.id"),nullable=False)

    allocated_amount = db.Column(db.Numeric(12, 2),nullable=False)

    __table_args__ = (
        db.UniqueConstraint("payment_id","invoice_id",name="unique_payment_invoice"),
    )

    def __repr__(self):
        return (
            f"<PaymentAllocation payment={self.payment_id} "
            f"invoice={self.invoice_id}>"
        )
