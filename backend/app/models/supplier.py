from app import db
from datetime import datetime, timezone


class Supplier(db.Model):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)

    business_name = db.Column(db.String(150), nullable=False)
    contact_person = db.Column(db.String(100))

    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120))

    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    pincode = db.Column(db.String(10))

    gstin = db.Column(db.String(15), unique=True)

    is_active = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<Supplier {self.business_name}>"
