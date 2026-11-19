from app import db


class ProductionConsumption(db.Model):
    __tablename__ = "production_consumptions"

    id = db.Column(db.Integer, primary_key=True)

    production_run_id = db.Column(db.Integer,db.ForeignKey("production_runs.id"),nullable=False)

    material_item_id = db.Column(db.Integer,db.ForeignKey("items.id"),nullable=False)

    planned_quantity = db.Column(db.Numeric(12, 3),nullable=False)

    actual_quantity = db.Column(db.Numeric(12, 3),nullable=False,default=0)

    unit_cost = db.Column(db.Numeric(12, 2),nullable=False,default=0)

    __table_args__ = (
        db.UniqueConstraint("production_run_id","material_item_id",name="unique_production_material"),
    )

    def __repr__(self):
        return (
            f"<ProductionConsumption "
            f"run={self.production_run_id} "
            f"material={self.material_item_id}>"
        )
