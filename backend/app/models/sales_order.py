from app import db
from datetime import datetime, timezone


class SalesOrder(db.Model):
    __tablename__ = "sales_orders"

    id = db.Column(db.Integer, primary_key=True)

    order_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=False
    )

    salesman_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    order_date = db.Column(db.Date, nullable=False)

    # DRAFT, SUBMITTED, APPROVED, REJECTED, CANCELLED
    status = db.Column(
        db.String(20),
        nullable=False,
        default="DRAFT"
    )

    subtotal = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=0
    )

    discount_amount = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=0
    )

    tax_amount = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=0
    )

    total_amount = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=0
    )

    notes = db.Column(db.Text)

    reviewed_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    reviewed_at = db.Column(
        db.DateTime(timezone=True)
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def __repr__(self):
        return f"<SalesOrder {self.order_number}>"
