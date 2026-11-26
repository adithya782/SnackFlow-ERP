
from app import db
from datetime import datetime, timezone


class ProductionOverhead(db.Model):
    __tablename__ = "production_overheads"

    id = db.Column(db.Integer, primary_key=True)

    production_run_id = db.Column(
        db.Integer,
        db.ForeignKey("production_runs.id"),
        nullable=False
    )

    category = db.Column(db.String(30), nullable=False)

    amount = db.Column(db.Numeric(12, 2), nullable=False)

    description = db.Column(db.Text)

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id")
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    __table_args__ = (
        db.CheckConstraint(
            "amount > 0",
            name="check_production_overhead_amount"
        ),
    )

    def __repr__(self):
        return (
            f"<ProductionOverhead "
            f"run={self.production_run_id} "
            f"category={self.category} "
            f"amount={self.amount}>"
        )
