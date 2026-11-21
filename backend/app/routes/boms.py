from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app import db
from app.models.bom import BOM
from app.models.bom_item import BOMItem
from app.models.item import Item
from app.services.bom_service import create_bom
from app.utils.decorators import role_required


boms_bp = Blueprint("boms", __name__, url_prefix="/api/boms")


def serialize_bom(bom):
    bom_items = BOMItem.query.filter_by(bom_id=bom.id).all()

    product = db.session.get(Item, bom.product_id)

    materials = []

    for entry in bom_items:
        material = db.session.get(Item, entry.material_item_id)

        materials.append({
            "material_item_id": entry.material_item_id,
            "material_name": material.name if material else None,
            "category": material.category if material else None,
            "quantity": str(entry.quantity),
            "unit": material.unit if material else None
        })

    return {
        "id": bom.id,
        "name": bom.name,
        "product_id": bom.product_id,
        "product_name": product.name if product else None,
        "output_quantity": str(bom.output_quantity),
        "materials": materials
    }


# GET: List all BOMs
@boms_bp.route("", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "PRODUCTION", "ACCOUNTANT")
def get_boms():
    boms = BOM.query.order_by(BOM.id.desc()).all()

    return jsonify({
        "status": "success",
        "count": len(boms),
        "boms": [serialize_bom(bom) for bom in boms]
    }), 200


# GET: Get one BOM
@boms_bp.route("/<int:bom_id>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "PRODUCTION", "ACCOUNTANT")
def get_bom(bom_id):
    bom = db.session.get(BOM, bom_id)

    if not bom:
        return jsonify({
            "status": "error",
            "message": "BOM not found."
        }), 404

    return jsonify({
        "status": "success",
        "bom": serialize_bom(bom)
    }), 200


# POST: Create a BOM
@boms_bp.route("", methods=["POST"])
@jwt_required()
@role_required("ADMIN")
def add_bom():
    data = request.get_json(silent=True) or {}

    try:
        bom = create_bom(data)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "BOM created successfully.",
            "bom": serialize_bom(bom)
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
            "message": "An unexpected error occurred while creating the BOM."
        }), 500
