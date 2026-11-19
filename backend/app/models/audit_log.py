from app import db
from datetime import datetime, timezone


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer,db.ForeignKey("users.id"))

    # CREATE, UPDATE, APPROVE, REJECT, DELETE, etc.
    action = db.Column(db.String(30),nullable=False)

    entity_type = db.Column(db.String(50),nullable=False)

    entity_id = db.Column(db.Integer)

    description = db.Column(db.Text)

    created_at = db.Column(db.DateTime(timezone=True),default=lambda: datetime.now(timezone.utc),nullable=False)

    def __repr__(self):
        return f"<AuditLog {self.action} {self.entity_type}>"
