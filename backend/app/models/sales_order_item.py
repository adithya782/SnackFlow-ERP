from app import db


class SalesOrderItem(db.Model):
    __tablename__ = "sales_order_items"

    id = db.Column(db.Integer, primary_key=True)

    sales_order_id = db.Column(
        db.Integer,
        db.ForeignKey("sales_orders.id"),
        nullable=False
    )

    item_id = db.Column(
        db.Integer,
        db.ForeignKey("items.id"),
        nullable=False
    )

    quantity = db.Column(
        db.Numeric(12, 3),
        nullable=False
    )

    unit_price = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    discount_amount = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=0
    )

    tax_rate = db.Column(
        db.Numeric(5, 2),
        nullable=False,
        default=0
    )

    tax_amount = db.Column(
        db.Numeric(12, 2),
        nullable=False,
        default=0
    )

    line_total = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    def __repr__(self):
        return f"<SalesOrderItem {self.item_id}>"
