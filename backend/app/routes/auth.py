
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)

from app.services.auth_service import authenticate_user, create_user
from app.models.user import User
from app.utils.decorators import role_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "status": "error",
            "message": "Email and password are required."
        }), 400

    user = authenticate_user(email, password)

    if not user:
        return jsonify({
            "status": "error",
            "message": "Invalid email or password."
        }), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )

    refresh_token = create_refresh_token(
        identity=str(user.id)
    )

    return jsonify({
        "status": "success",
        "message": "Login successful.",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), 200

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_access_token():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user or not user.is_active:
        return jsonify({
            "status": "error",
            "message": "User not found or inactive."
        }), 401

    new_access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )

    return jsonify({
        "status": "success",
        "access_token": new_access_token
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user or not user.is_active:
        return jsonify({
            "status": "error",
            "message": "User not found or inactive."
        }), 404

    return jsonify({
        "status": "success",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), 200


@auth_bp.route("/users", methods=["GET"])
@role_required("ADMIN")
def get_employees():
    employees = User.query.order_by(User.id.asc()).all()

    return jsonify({
        "status": "success",
        "count": len(employees),
        "employees": [
            {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active,
                "created_at": (
                    user.created_at.isoformat()
                    if user.created_at else None
                )
            }
            for user in employees
        ]
    }), 200


@auth_bp.route("/users", methods=["POST"])
@role_required("ADMIN")
def create_employee():
    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    role = data.get("role", "").strip().upper()

    if not name or not email or not password or not role:
        return jsonify({
            "status": "error",
            "message": "Name, email, password and role are required."
        }), 400

    allowed_roles = ["SALESMAN", "PRODUCTION", "ACCOUNTANT"]

    if role not in allowed_roles:
        return jsonify({
            "status": "error",
            "message": "Invalid employee role."
        }), 400

    if len(password) < 8:
        return jsonify({
            "status": "error",
            "message": "Password must contain at least 8 characters."
        }), 400

    try:
        user = create_user(name, email, password, role)

        return jsonify({
            "status": "success",
            "message": "Employee created successfully.",
            "employee": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "is_active": user.is_active
            }
        }), 201

    except ValueError as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 409


@auth_bp.route("/users/<int:user_id>/status", methods=["PATCH"])
@role_required("ADMIN")
def update_employee_status(user_id):
    data = request.get_json(silent=True) or {}

    if "is_active" not in data or not isinstance(
        data["is_active"], bool
    ):
        return jsonify({
            "status": "error",
            "message": "A boolean is_active value is required."
        }), 400

    current_user_id = int(get_jwt_identity())

    if user_id == current_user_id and data["is_active"] is False:
        return jsonify({
            "status": "error",
            "message": "You cannot deactivate your own account."
        }), 400

    employee = User.query.get(user_id)

    if not employee:
        return jsonify({
            "status": "error",
            "message": "Employee not found."
        }), 404

    employee.is_active = data["is_active"]
    from app import db
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Employee status updated successfully.",
        "employee": {
            "id": employee.id,
            "name": employee.name,
            "email": employee.email,
            "role": employee.role,
            "is_active": employee.is_active
        }
    }), 200


@auth_bp.route("/admin-test", methods=["GET"])
@role_required("ADMIN")
def admin_test():
    return jsonify({
        "status": "success",
        "message": "Welcome, Admin!"
    }), 200
