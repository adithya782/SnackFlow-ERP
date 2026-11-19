from app import db
from datetime import datetime, timezone


class BOM(db.Model):
    __tablename__ = "boms"

    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(db.Integer,db.ForeignKey("items.id"),nullable=False)

    name = db.Column(db.String(150), nullable=False)

    output_quantity = db.Column(db.Numeric(12, 3), nullable=False)

    is_active = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<BOM {self.name}>"
