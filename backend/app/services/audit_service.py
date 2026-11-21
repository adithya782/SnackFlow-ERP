
from app import db
from app.models.audit_log import AuditLog


def log_action(user_id, action, entity_type, entity_id, description=None):
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description
    )

    db.session.add(audit_log)
    db.session.flush()

    return audit_log
