from app import db
from sqlalchemy import Numeric


class PurchaseItem(db.Model):
    __tablename__ = "purchase_items"

    id = db.Column(db.Integer, primary_key=True)

    purchase_id = db.Column(
        db.Integer,
        db.ForeignKey("purchases.id"),
        nullable=False
    )

    item_id = db.Column(
        db.Integer,
        db.ForeignKey("items.id"),
        nullable=False
    )

    quantity = db.Column(Numeric(12, 3), nullable=False)

    unit_price = db.Column(Numeric(12, 2), nullable=False)

    tax_rate = db.Column(Numeric(5, 2), nullable=False, default=0)

    tax_amount = db.Column(Numeric(12, 2), nullable=False, default=0)

    line_total = db.Column(Numeric(12, 2), nullable=False)

    def __repr__(self):
        return f"<PurchaseItem {self.item_id}>"
