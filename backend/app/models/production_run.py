from app import db
from datetime import datetime, timezone


class ProductionRun(db.Model):
    __tablename__ = "production_runs"

    id = db.Column(db.Integer, primary_key=True)

    run_number = db.Column(db.String(50), unique=True, nullable=False)

    bom_id = db.Column(db.Integer, db.ForeignKey("boms.id"), nullable=False)

    planned_output = db.Column(db.Numeric(12, 3), nullable=False)

    actual_output = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    production_date = db.Column(db.Date, nullable=False)

    # PLANNED, IN_PROGRESS, COMPLETED, CANCELLED
    status = db.Column(db.String(20), nullable=False, default="PLANNED")

    notes = db.Column(db.Text)

    created_by = db.Column(db.Integer, db.ForeignKey("users.id"))

    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def __repr__(self):
        return f"<ProductionRun {self.run_number}>"

