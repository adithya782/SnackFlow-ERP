from app import db
from datetime import datetime, timezone


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

    payment_number = db.Column(db.String(50),unique=True,nullable=False)

    customer_id = db.Column(db.Integer,db.ForeignKey("customers.id"),nullable=False)

    payment_date = db.Column(db.Date, nullable=False)

    amount = db.Column(db.Numeric(12, 2),nullable=False)

    # CASH, UPI, BANK_TRANSFER, CHEQUE, OTHER
    payment_method = db.Column(db.String(30),nullable=False)

    reference_number = db.Column(db.String(100))

    # RECEIVED, VOID
    status = db.Column(db.String(20),nullable=False,default="RECEIVED")

    notes = db.Column(db.Text)

    received_by = db.Column(db.Integer,db.ForeignKey("users.id"))

    created_at = db.Column(db.DateTime(timezone=True),default=lambda: datetime.now(timezone.utc),nullable=False)

    def __repr__(self):
        return f"<Payment {self.payment_number}>"
