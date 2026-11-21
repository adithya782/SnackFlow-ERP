
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.audit_service import log_action

from app import db
from app.models.payment import Payment
from app.models.payment_allocation import PaymentAllocation
from app.services.payment_service import (
    create_payment,
    allocate_payment,
    get_invoice_outstanding
)
from app.utils.decorators import role_required


payments_bp = Blueprint("payments", __name__, url_prefix="/api/payments")


def serialize_payment(payment):
    return {
        "id": payment.id,
        "payment_number": payment.payment_number,
        "customer_id": payment.customer_id,
        "payment_date": payment.payment_date.isoformat(),
        "amount": str(payment.amount),
        "payment_method": payment.payment_method,
        "reference_number": payment.reference_number,
        "status": payment.status,
        "notes": payment.notes,
        "received_by": payment.received_by
    }


@payments_bp.route("", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT")
def get_payments():
    payments = Payment.query.order_by(Payment.id.desc()).all()

    return jsonify([
        serialize_payment(payment)
        for payment in payments
    ]), 200


@payments_bp.route("/<int:payment_id>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT")
def get_payment(payment_id):
    payment = db.session.get(Payment, payment_id)

    if not payment:
        return jsonify({"message": "Payment not found."}), 404

    return jsonify(serialize_payment(payment)), 200


@payments_bp.route("", methods=["POST"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT")
def create_payment_route():
    data = request.get_json() or {}
    user_id = int(get_jwt_identity())

    try:
        payment = create_payment(data, user_id)
        log_action(
            user_id=user_id,
            action="RECEIVE",
            entity_type="PAYMENT",
            entity_id=payment.id,
            description=f"Payment {payment.payment_number} received."
        )
        db.session.commit()

        return jsonify({
            "message": "Payment recorded successfully.",
            "payment": serialize_payment(payment)
        }), 201

    except ValueError as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 400

    except Exception:
        db.session.rollback()
        return jsonify({"message": "Unable to record payment."}), 500


@payments_bp.route("/<int:payment_id>/allocate", methods=["POST"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT")
def allocate_payment_route(payment_id):
    data = request.get_json() or {}

    try:
        allocation = allocate_payment(payment_id, data)
        db.session.commit()

        return jsonify({
            "message": "Payment allocated successfully.",
            "allocation": {
                "id": allocation.id,
                "payment_id": allocation.payment_id,
                "invoice_id": allocation.invoice_id,
                "allocated_amount": str(allocation.allocated_amount)
            }
        }), 200

    except ValueError as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 400

    except Exception:
        db.session.rollback()
        return jsonify({"message": "Unable to allocate payment."}), 500


@payments_bp.route("/invoice/<int:invoice_id>/outstanding", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT")
def invoice_outstanding_route(invoice_id):
    try:
        result = get_invoice_outstanding(invoice_id)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"message": str(e)}), 404
