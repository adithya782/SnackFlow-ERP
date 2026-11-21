from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.models.item import Item
from app.models.stock_movement import StockMovement
from app.services.inventory_service import (
    get_item_stock,
    record_stock_movement
)
from app.utils.decorators import role_required

inventory_bp = Blueprint(
    "inventory",
    __name__,
    url_prefix="/api/inventory"
)

VIEW_ROLES = ("ADMIN", "SALESMAN", "PRODUCTION", "ACCOUNTANT")


def serialize_movement(movement):
    return {
        "id": movement.id,
        "item_id": movement.item_id,
        "movement_type": movement.movement_type,
        "quantity": str(movement.quantity),
        "reference_type": movement.reference_type,
        "reference_id": movement.reference_id,
        "notes": movement.notes,
        "created_at": movement.created_at.isoformat()
    }


@inventory_bp.route("/stock", methods=["GET"])
@jwt_required()
@role_required(*VIEW_ROLES)
def get_all_stock():
    items = Item.query.filter_by(is_active=True).order_by(Item.id).all()

    stock_data = []

    for item in items:
        stock_data.append({
            "item_id": item.id,
            "name": item.name,
            "sku": item.sku,
            "category": item.category,
            "unit": item.unit,
            "current_stock": str(get_item_stock(item.id)),
            "reorder_level": str(item.reorder_level)
        })

    return jsonify({
        "status": "success",
        "count": len(stock_data),
        "stock": stock_data
    }), 200


@inventory_bp.route("/stock/<int:item_id>", methods=["GET"])
@jwt_required()
@role_required(*VIEW_ROLES)
def get_item_stock_details(item_id):
    item = db.session.get(Item, item_id)

    if not item:
        return jsonify({"message": "Item not found."}), 404

    return jsonify({
        "status": "success",
        "item": {
            "id": item.id,
            "name": item.name,
            "sku": item.sku,
            "unit": item.unit,
            "current_stock": str(get_item_stock(item_id))
        }
    }), 200


@inventory_bp.route("/movements", methods=["GET"])
@jwt_required()
@role_required(*VIEW_ROLES)
def get_stock_movements():
    item_id = request.args.get("item_id", type=int)

    query = StockMovement.query

    if item_id is not None:
        query = query.filter_by(item_id=item_id)

    movements = query.order_by(
        StockMovement.created_at.desc()
    ).limit(100).all()

    return jsonify({
        "status": "success",
        "count": len(movements),
        "movements": [
            serialize_movement(m) for m in movements
        ]
    }), 200


@inventory_bp.route("/movements", methods=["POST"])
@jwt_required()
@role_required("ADMIN")
def create_stock_movement():
    data = request.get_json(silent=True) or {}

    required = [
        "item_id", "movement_type",
        "quantity", "reference_type"
    ]

    for field in required:
        if field not in data:
            return jsonify({
                "message": f"{field} is required."
            }), 400

    try:
        movement = record_stock_movement(
            item_id=data["item_id"],
            movement_type=data["movement_type"],
            quantity=data["quantity"],
            reference_type=data["reference_type"],
            reference_id=data.get("reference_id"),
            notes=data.get("notes"),
            created_by=int(get_jwt_identity())
        )

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Stock movement recorded.",
            "movement": serialize_movement(movement)
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
            "message": "Could not record stock movement."
        }), 500
