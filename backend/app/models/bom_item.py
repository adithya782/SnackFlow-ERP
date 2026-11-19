from app import db


class BOMItem(db.Model):
    __tablename__ = "bom_items"

    id = db.Column(db.Integer, primary_key=True)

    bom_id = db.Column(db.Integer,db.ForeignKey("boms.id"),nullable=False)

    material_item_id = db.Column(db.Integer,db.ForeignKey("items.id"),nullable=False)

    quantity = db.Column(db.Numeric(12, 3), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("bom_id","material_item_id",name="unique_bom_material"),
    )

    def __repr__(self):
        return f"<BOMItem {self.material_item_id}>"
