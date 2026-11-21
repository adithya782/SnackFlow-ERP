from datetime import datetime, timezone

from app import db


class CompanySettings(db.Model):
    __tablename__ = "company_settings"

    id = db.Column(db.Integer, primary_key=True)

    business_name = db.Column(db.String(150), nullable=False)
    gstin = db.Column(db.String(15), unique=True, nullable=True)

    address = db.Column(db.String(250), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=True)

    phone = db.Column(db.String(15), nullable=True)
    email = db.Column(db.String(120), nullable=True)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
