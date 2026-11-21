from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app import db
from app.models.customer import Customer
from app.utils.decorators import role_required

customers_bp = Blueprint(
    "customers",
    __name__,
    url_prefix="/api/customers"
)

VIEW_ROLES = ("ADMIN", "SALESMAN", "ACCOUNTANT")


def serialize_customer(customer):
    return {
        "id": customer.id,
        "business_name": customer.business_name,
        "contact_person": customer.contact_person,
        "phone": customer.phone,
        "email": customer.email,
        "address": customer.address,
        "city": customer.city,
        "state": customer.state,
        "pincode": customer.pincode,
        "gstin": customer.gstin,
        "is_active": customer.is_active
    }


@customers_bp.route("", methods=["GET"])
@jwt_required()
@role_required(*VIEW_ROLES)
def get_customers():
    customers = Customer.query.order_by(Customer.id.desc()).all()

    return jsonify({
        "status": "success",
        "count": len(customers),
        "customers": [serialize_customer(c) for c in customers]
    }), 200


@customers_bp.route("/<int:customer_id>", methods=["GET"])
@jwt_required()
@role_required(*VIEW_ROLES)
def get_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"message": "Customer not found."}), 404

    return jsonify({
        "status": "success",
        "customer": serialize_customer(customer)
    }), 200


@customers_bp.route("", methods=["POST"])
@jwt_required()
@role_required("ADMIN")
def create_customer():
    data = request.get_json(silent=True) or {}

    required = ["business_name", "phone"]

    for field in required:
        if not isinstance(data.get(field), str) or not data[field].strip():
            return jsonify({
                "status": "error",
                "message": f"{field} is required."
            }), 400

    gstin = data.get("gstin")
    if gstin is not None:
        if not isinstance(gstin, str):
            return jsonify({"message": "Invalid GSTIN."}), 400
        gstin = gstin.strip().upper() or None

    if gstin and Customer.query.filter_by(gstin=gstin).first():
        return jsonify({"message": "GSTIN already exists."}), 409

    customer = Customer(
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
        db.session.add(customer)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "Could not create customer."}), 400

    return jsonify({
        "status": "success",
        "message": "Customer created successfully.",
        "customer": serialize_customer(customer)
    }), 201


@customers_bp.route("/<int:customer_id>", methods=["PUT"])
@jwt_required()
@role_required("ADMIN")
def update_customer(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"message": "Customer not found."}), 404

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

            setattr(customer, field, value)

    if "gstin" in data:
        gstin = data["gstin"]

        if gstin is not None and not isinstance(gstin, str):
            return jsonify({"message": "Invalid GSTIN."}), 400

        gstin = gstin.strip().upper() if gstin else None

        existing = Customer.query.filter(
            Customer.gstin == gstin,
            Customer.id != customer_id
        ).first() if gstin else None

        if existing:
            return jsonify({"message": "GSTIN already exists."}), 409

        customer.gstin = gstin

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"message": "Could not update customer."}), 400

    return jsonify({
        "status": "success",
        "message": "Customer updated successfully.",
        "customer": serialize_customer(customer)
    }), 200


@customers_bp.route("/<int:customer_id>/status", methods=["PATCH"])
@jwt_required()
@role_required("ADMIN")
def update_customer_status(customer_id):
    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"message": "Customer not found."}), 404

    data = request.get_json(silent=True) or {}

    if not isinstance(data.get("is_active"), bool):
        return jsonify({"message": "is_active must be true or false."}), 400

    customer.is_active = data["is_active"]
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Customer status updated.",
        "customer": serialize_customer(customer)
    }), 200
