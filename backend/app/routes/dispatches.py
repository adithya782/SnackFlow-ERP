
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.audit_service import log_action

from app import db
from app.models.dispatch import Dispatch
from app.services.dispatch_service import create_dispatch, dispatch_goods
from app.utils.decorators import role_required


dispatches_bp = Blueprint("dispatches", __name__, url_prefix="/api/dispatches")


def serialize_dispatch(dispatch):
    return {
        "id": dispatch.id,
        "dispatch_number": dispatch.dispatch_number,
        "invoice_id": dispatch.invoice_id,
        "dispatch_date": dispatch.dispatch_date.isoformat(),
        "transporter_name": dispatch.transporter_name,
        "vehicle_number": dispatch.vehicle_number,
        "tracking_number": dispatch.tracking_number,
        "status": dispatch.status,
        "notes": dispatch.notes,
        "dispatched_by": dispatch.dispatched_by
    }


@dispatches_bp.route("", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT", "PRODUCTION")
def get_dispatches():
    dispatches = Dispatch.query.order_by(
        Dispatch.id.desc()
    ).all()

    return jsonify([
        serialize_dispatch(dispatch)
        for dispatch in dispatches
    ]), 200


@dispatches_bp.route("/<int:dispatch_id>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT", "PRODUCTION")
def get_dispatch(dispatch_id):
    dispatch = db.session.get(Dispatch, dispatch_id)

    if not dispatch:
        return jsonify({"message": "Dispatch not found."}), 404

    return jsonify(serialize_dispatch(dispatch)), 200


@dispatches_bp.route("", methods=["POST"])
@jwt_required()
@role_required("ADMIN", "PRODUCTION")
def create_dispatch_route():
    data = request.get_json() or {}
    user_id = int(get_jwt_identity())

    try:
        dispatch = create_dispatch(data, user_id)
        db.session.commit()

        return jsonify({
            "message": "Dispatch created successfully.",
            "dispatch": serialize_dispatch(dispatch)
        }), 201

    except ValueError as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 400

    except Exception:
        db.session.rollback()
        return jsonify({"message": "Unable to create dispatch."}), 500


@dispatches_bp.route("/<int:dispatch_id>/dispatch", methods=["POST"])
@jwt_required()
@role_required("ADMIN", "PRODUCTION")
def dispatch_goods_route(dispatch_id):
    user_id = int(get_jwt_identity())

    try:
        dispatch = dispatch_goods(dispatch_id, user_id)
        log_action(
            user_id=user_id,
            action="DISPATCH",
            entity_type="DISPATCH",
            entity_id=dispatch.id,
            description=f"Goods dispatched through {dispatch.dispatch_number}."
        )
        db.session.commit()

        return jsonify({
            "message": "Goods dispatched successfully. Inventory updated.",
            "dispatch": serialize_dispatch(dispatch)
        }), 200

    except ValueError as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 400

    except Exception:
        import traceback
        traceback.print_exc()

        db.session.rollback()
        return jsonify({
            "message": "Unable to dispatch goods."
        }), 500
