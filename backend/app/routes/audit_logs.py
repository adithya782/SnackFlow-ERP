
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.models.audit_log import AuditLog
from app.utils.decorators import role_required


audit_logs_bp = Blueprint(
    "audit_logs",
    __name__,
    url_prefix="/api/audit-logs"
)


@audit_logs_bp.route("", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT")
def get_audit_logs():
    logs = AuditLog.query.order_by(
        AuditLog.created_at.desc()
    ).limit(200).all()

    return jsonify([
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "description": log.description,
            "created_at": log.created_at.isoformat()
        }
        for log in logs
    ]), 200
