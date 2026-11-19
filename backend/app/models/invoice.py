from app import db
from datetime import datetime, timezone


class Invoice(db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)

    invoice_number = db.Column(db.String(50),unique=True,nullable=False)

    sales_order_id = db.Column(db.Integer,db.ForeignKey("sales_orders.id"),unique=True, nullable=False)

    customer_id = db.Column(db.Integer,db.ForeignKey("customers.id"),nullable=False)

    invoice_date = db.Column(db.Date, nullable=False)

    taxable_amount = db.Column(db.Numeric(12, 2),nullable=False,default=0)

    cgst_amount = db.Column(db.Numeric(12, 2),nullable=False,default=0)

    sgst_amount = db.Column(db.Numeric(12, 2),nullable=False,default=0)

    igst_amount = db.Column(db.Numeric(12, 2),nullable=False,default=0)

    total_tax = db.Column(db.Numeric(12, 2),nullable=False,default=0)

    total_amount = db.Column(db.Numeric(12, 2),nullable=False,default=0)

    # DRAFT, ISSUED, CANCELLED
    status = db.Column(db.String(20),nullable=False,default="DRAFT")

    notes = db.Column(db.Text)

    created_by = db.Column(db.Integer,db.ForeignKey("users.id"))

    created_at = db.Column(db.DateTime(timezone=True),default=lambda: datetime.now(timezone.utc),nullable=False)

    def __repr__(self):
        return f"<Invoice {self.invoice_number}>"
