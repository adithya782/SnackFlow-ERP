from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app import db
from app.models.supplier import Supplier
from app.utils.decorators import role_required

suppliers_bp = Blueprint(
    "suppliers",
    __name__,
    url_prefix="/api/suppliers"
)

VIEW_ROLES = ("ADMIN", "PRODUCTION", "ACCOUNTANT")


def serialize_supplier(supplier):
    return {
        "id": supplier.id,
        "business_name": supplier.business_name,
        "contact_person": supplier.contact_person,
        "phone": supplier.phone,
        "email": supplier.email,
        "address": supplier.address,
        "city": supplier.city,
        "state": supplier.state,
        "pincode": supplier.pincode,
        "gstin": supplier.gstin,
        "is_active": supplier.is_active
    }


@suppliers_bp.route("", methods=["GET"])
@jwt_required()
@role_required(*VIEW_ROLES)
def get_suppliers():
    suppliers = Supplier.query.order_by(Supplier.id.desc()).all()

    return jsonify({
        "status": "success",
        "count": len(suppliers),
        "suppliers": [serialize_supplier(s) for s in suppliers]
    }), 200


@suppliers_bp.route("/<int:supplier_id>", methods=["GET"])
@jwt_required()
@role_required(*VIEW_ROLES)
def get_supplier(supplier_id):
    supplier = db.session.get(Supplier, supplier_id)

    if not supplier:
        return jsonify({"message": "Supplier not found."}), 404

    return jsonify({
        "status": "success",
        "supplier": serialize_supplier(supplier)
    }), 200


@suppliers_bp.route("", methods=["POST"])
@jwt_required()
@role_required("ADMIN")
def create_supplier():
    data = request.get_json(silent=True) or {}

    for field in ["business_name", "phone"]:
        if not isinstance(data.get(field), str) or not data[field].strip():
            return jsonify({
                "message": f"{field} is required."
            }), 400

    gstin = data.get("gstin")

    if gstin is not None and not isinstance(gstin, str):
        return jsonify({"message": "Invalid GSTIN."}), 400

    gstin = gstin.strip().upper() if gstin else None

    if gstin and Supplier.query.filter_by(gstin=gstin).first():
        return jsonify({"message": "GSTIN already exists."}), 409

    supplier = Supplier(
        business_name=data["business_name"].strip(),
        contact_person=data.get("contact_person"),
        phone=data["phone"].strip(),
        email=data.get("email"),
        address=data.get("address"),
        city=data.get("city"),
        state=data.get("state"),
        pincode=data.get("pincode"),
        gstin=gstin
    )

    try:
        db.session.add(supplier)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "Could not create supplier."}), 400

    return jsonify({
        "status": "success",
        "message": "Supplier created successfully.",
        "supplier": serialize_supplier(supplier)
    }), 201


@suppliers_bp.route("/<int:supplier_id>", methods=["PUT"])
@jwt_required()
@role_required("ADMIN")
def update_supplier(supplier_id):
    supplier = db.session.get(Supplier, supplier_id)

    if not supplier:
        return jsonify({"message": "Supplier not found."}), 404

    data = request.get_json(silent=True) or {}

    fields = [
        "business_name", "contact_person", "phone", "email",
        "address", "city", "state", "pincode"
    ]

    for field in fields:
        if field in data:
            value = data[field]

            if field in ("business_name", "phone"):
                if not isinstance(value, str) or not value.strip():
                    return jsonify({"message": f"Invalid {field}."}), 400
                value = value.strip()

            setattr(supplier, field, value)

    if "gstin" in data:
        gstin = data["gstin"]

        if gstin is not None and not isinstance(gstin, str):
            return jsonify({"message": "Invalid GSTIN."}), 400

        gstin = gstin.strip().upper() if gstin else None

        existing = Supplier.query.filter(
            Supplier.gstin == gstin,
            Supplier.id != supplier_id
        ).first() if gstin else None

        if existing:
            return jsonify({"message": "GSTIN already exists."}), 409

        supplier.gstin = gstin

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "Could not update supplier."}), 400

    return jsonify({
        "status": "success",
        "message": "Supplier updated successfully.",
        "supplier": serialize_supplier(supplier)
    }), 200


@suppliers_bp.route("/<int:supplier_id>/status", methods=["PATCH"])
@jwt_required()
@role_required("ADMIN")
def update_supplier_status(supplier_id):
    supplier = db.session.get(Supplier, supplier_id)

    if not supplier:
        return jsonify({"message": "Supplier not found."}), 404

    data = request.get_json(silent=True) or {}

    if not isinstance(data.get("is_active"), bool):
        return jsonify({"message": "is_active must be true or false."}), 400

    supplier.is_active = data["is_active"]
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Supplier status updated.",
        "supplier": serialize_supplier(supplier)
    }), 200
