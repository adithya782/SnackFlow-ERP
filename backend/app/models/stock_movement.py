from app import db
from datetime import datetime, timezone


class StockMovement(db.Model):
    __tablename__ = "stock_movements"

    id = db.Column(db.Integer, primary_key=True)

    item_id = db.Column(db.Integer,db.ForeignKey("items.id"),nullable=False)

    movement_type = db.Column(db.String(10), nullable=False)

    quantity = db.Column(db.Numeric(12, 3), nullable=False)

    reference_type = db.Column(db.String(30), nullable=False)

    reference_id = db.Column(db.Integer)

    notes = db.Column(db.Text)

    created_by = db.Column(db.Integer,db.ForeignKey("users.id"))

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def __repr__(self):
        return (
            f"<StockMovement item={self.item_id} "
            f"type={self.movement_type} qty={self.quantity}>"
        )
