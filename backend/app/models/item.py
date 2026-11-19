from app import db
from datetime import datetime, timezone


class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)

    category = db.Column(db.String(30), nullable=False)

    unit = db.Column(db.String(20), nullable=False)

    description = db.Column(db.Text)

    reorder_level = db.Column(db.Numeric(12, 3), default=0)

    is_active = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Item {self.name}>"
