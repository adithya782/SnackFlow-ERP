from app import db
from datetime import datetime, timezone


class Dispatch(db.Model):
    __tablename__ = "dispatches"

    id = db.Column(db.Integer, primary_key=True)

    dispatch_number = db.Column(db.String(50),unique=True,nullable=False)

    invoice_id = db.Column(db.Integer,db.ForeignKey("invoices.id"),unique=True,nullable=False)

    dispatch_date = db.Column(db.Date, nullable=False)

    transporter_name = db.Column(db.String(150))

    vehicle_number = db.Column(db.String(30))

    tracking_number = db.Column(db.String(100))

    # PREPARED, DISPATCHED, DELIVERED, CANCELLED
    status = db.Column(db.String(20),nullable=False,default="PREPARED")

    notes = db.Column(db.Text)

    dispatched_by = db.Column(db.Integer,db.ForeignKey("users.id"))

    created_at = db.Column(db.DateTime(timezone=True),default=lambda: datetime.now(timezone.utc),nullable=False)

    def __repr__(self):
        return f"<Dispatch {self.dispatch_number}>"
