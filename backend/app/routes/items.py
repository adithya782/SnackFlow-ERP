from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app import db
from app.models.item import Item
from app.utils.decorators import role_required

items_bp = Blueprint("items", __name__, url_prefix="/api/items")

ALLOWED_CATEGORIES = {
    "FINISHED_GOOD",
    "RAW_MATERIAL",
    "PACKAGING"
}

ALLOWED_ROLES = ("ADMIN", "SALESMAN", "PRODUCTION", "ACCOUNTANT")


def serialize_item(item):
    return {
        "id": item.id,
        "name": item.name,
        "sku": item.sku,
        "category": item.category,
        "unit": item.unit,
        "description": item.description,
        "reorder_level": str(item.reorder_level),
        "is_active": item.is_active
    }


@items_bp.route("", methods=["GET"])
@jwt_required()
@role_required(*ALLOWED_ROLES)
def get_items():
    items = Item.query.order_by(Item.id.desc()).all()

    return jsonify({
        "status": "success",
        "count": len(items),
        "items": [serialize_item(item) for item in items]
    }), 200


@items_bp.route("", methods=["POST"])
@jwt_required()
@role_required("ADMIN")
def create_item():
    data = request.get_json(silent=True) or {}

    required_fields = ["name", "sku", "category", "unit"]

    for field in required_fields:
        if not data.get(field):
            return jsonify({
                "status": "error",
                "message": f"{field} is required."
            }), 400

    name = data["name"].strip()
    sku = data["sku"].strip().upper()
    category = data["category"].strip().upper()
    unit = data["unit"].strip()

    if not name or not sku or not unit:
        return jsonify({
            "status": "error",
            "message": "Name, SKU and unit cannot be empty."
        }), 400

    if category not in ALLOWED_CATEGORIES:
        return jsonify({
            "status": "error",
            "message": "Invalid item category."
        }), 400

    if Item.query.filter_by(sku=sku).first():
        return jsonify({
            "status": "error",
            "message": "SKU already exists."
        }), 409

    item = Item(
        name=name,
        sku=sku,
        category=category,
        unit=unit,
        description=data.get("description"),
        reorder_level=data.get("reorder_level", 0)
    )

    try:
        db.session.add(item)
        db.session.commit()

    except Exception:
        db.session.rollback()
        return jsonify({
            "status": "error",
            "message": "Could not create item. Check the submitted values."
        }), 400

    return jsonify({
        "status": "success",
        "message": "Item created successfully.",
        "item": serialize_item(item)
    }), 201



@items_bp.route("/<int:item_id>", methods=["GET"])
@jwt_required()
@role_required(*ALLOWED_ROLES)
def get_item(item_id):
    item = db.session.get(Item, item_id)

    if not item:
        return jsonify({
            "status": "error",
            "message": "Item not found."
        }), 404

    return jsonify({
        "status": "success",
        "item": serialize_item(item)
    }), 200


@items_bp.route("/<int:item_id>", methods=["PUT"])
@jwt_required()
@role_required("ADMIN")
def update_item(item_id):
    item = db.session.get(Item, item_id)

    if not item:
        return jsonify({
            "status": "error",
            "message": "Item not found."
        }), 404

    data = request.get_json(silent=True) or {}

    if "name" in data:
        if not isinstance(data["name"], str) or not data["name"].strip():
            return jsonify({"message": "Invalid name."}), 400
        item.name = data["name"].strip()

    if "sku" in data:
        if not isinstance(data["sku"], str) or not data["sku"].strip():
            return jsonify({"message": "Invalid SKU."}), 400

        new_sku = data["sku"].strip().upper()
        existing = Item.query.filter(
            Item.sku == new_sku,
            Item.id != item_id
        ).first()

        if existing:
            return jsonify({"message": "SKU already exists."}), 409

        item.sku = new_sku

    if "category" in data:
        category = data["category"].strip().upper()
        if category not in ALLOWED_CATEGORIES:
            return jsonify({"message": "Invalid category."}), 400
        item.category = category

    if "unit" in data:
        if not isinstance(data["unit"], str) or not data["unit"].strip():
            return jsonify({"message": "Invalid unit."}), 400
        item.unit = data["unit"].strip()

    if "description" in data:
        item.description = data["description"]

    if "reorder_level" in data:
        item.reorder_level = data["reorder_level"]

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "Could not update item."}), 400

    return jsonify({
        "status": "success",
        "message": "Item updated successfully.",
        "item": serialize_item(item)
    }), 200


@items_bp.route("/<int:item_id>/status", methods=["PATCH"])
@jwt_required()
@role_required("ADMIN")
def update_item_status(item_id):
    item = db.session.get(Item, item_id)

    if not item:
        return jsonify({"message": "Item not found."}), 404

    data = request.get_json(silent=True) or {}

    if not isinstance(data.get("is_active"), bool):
        return jsonify({
            "message": "is_active must be true or false."
        }), 400

    item.is_active = data["is_active"]
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Item status updated.",
        "item": serialize_item(item)
    }), 200
