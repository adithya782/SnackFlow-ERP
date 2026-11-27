from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models.supplier import Supplier

from app import db
from app.models.purchase import Purchase
from app.models.purchase_item import PurchaseItem
from app.services.purchase_service import (
    create_purchase,
    receive_purchase
)
from app.utils.decorators import role_required


purchases_bp = Blueprint("purchases", __name__, url_prefix="/api/purchases")


def serialize_purchase_item(item):
    return {
        "id": item.id,
        "item_id": item.item_id,
        "quantity": str(item.quantity),
        "unit_price": str(item.unit_price),
        "tax_rate": str(item.tax_rate),
        "tax_amount": str(item.tax_amount),
        "line_total": str(item.line_total)
    }


def serialize_purchase(purchase):
    items = PurchaseItem.query.filter_by(
        purchase_id=purchase.id
    ).all()
    supplier = db.session.get(Supplier, purchase.supplier_id)

    return {
        "id": purchase.id,
        "purchase_number": purchase.purchase_number,
        "supplier_id": purchase.supplier_id,
        "purchase_date": purchase.purchase_date.isoformat(),
        "supplier_invoice_number": purchase.supplier_invoice_number,
        "subtotal": str(purchase.subtotal),
        "tax_amount": str(purchase.tax_amount),
        "total_amount": str(purchase.total_amount),
        "status": purchase.status,
        "notes": purchase.notes,
        "created_by": purchase.created_by,
        "created_at": (
            purchase.created_at.isoformat()
            if purchase.created_at else None
        ),
        "items": [serialize_purchase_item(item) for item in items],
        "supplier_name": supplier.business_name if supplier else None,
    }


# GET: List all purchases
@purchases_bp.route("", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT", "PRODUCTION")
def get_purchases():
    purchases = Purchase.query.order_by(
        Purchase.id.desc()
    ).all()

    return jsonify({
        "status": "success",
        "count": len(purchases),
        "purchases": [
            serialize_purchase(purchase)
            for purchase in purchases
        ]
    }), 200


# GET: Get a specific purchase
@purchases_bp.route("/<int:purchase_id>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT", "PRODUCTION")
def get_purchase(purchase_id):
    purchase = db.session.get(Purchase, purchase_id)

    if not purchase:
        return jsonify({
            "status": "error",
            "message": "Purchase not found."
        }), 404

    return jsonify({
        "status": "success",
        "purchase": serialize_purchase(purchase)
    }), 200


# POST: Create a new draft purchase
@purchases_bp.route("", methods=["POST"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT")
def add_purchase():
    data = request.get_json(silent=True) or {}

    try:
        user_id = int(get_jwt_identity())

        purchase = create_purchase(data, user_id)

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Purchase created successfully.",
            "purchase": serialize_purchase(purchase)
        }), 201

    except (ValueError, TypeError) as error:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400

    except Exception:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred while creating the purchase."
        }), 500


# POST: Receive a purchase and update inventory
@purchases_bp.route("/<int:purchase_id>/receive", methods=["POST"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT")
def receive_purchase_route(purchase_id):
    try:
        user_id = int(get_jwt_identity())

        purchase = receive_purchase(purchase_id, user_id)

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Purchase received. Inventory updated successfully.",
            "purchase": serialize_purchase(purchase)
        }), 200

    except ValueError as error:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400

    except Exception:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred while receiving the purchase."
        }), 500
