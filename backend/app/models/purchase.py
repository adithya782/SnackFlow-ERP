from app import db
from datetime import datetime, timezone
from sqlalchemy import Numeric


class Purchase(db.Model):
    __tablename__ = "purchases"

    id = db.Column(db.Integer, primary_key=True)

    purchase_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    supplier_id = db.Column(
        db.Integer,
        db.ForeignKey("suppliers.id"),
        nullable=False
    )

    purchase_date = db.Column(
        db.Date,
        nullable=False
    )

    supplier_invoice_number = db.Column(db.String(100))

    subtotal = db.Column(Numeric(12, 2), nullable=False, default=0)

    tax_amount = db.Column(Numeric(12, 2), nullable=False, default=0)

    total_amount = db.Column(Numeric(12, 2), nullable=False, default=0)

    status = db.Column(
        db.String(20),
        nullable=False,
        default="DRAFT"
    )

    notes = db.Column(db.Text)

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def __repr__(self):
        return f"<Purchase {self.purchase_number}>"
