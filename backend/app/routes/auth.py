from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from app.services.auth_service import authenticate_user

from flask_jwt_extended import jwt_required, get_jwt_identity
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

    return jsonify({
        "status": "success",
        "message": "Login successful.",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
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


@auth_bp.route("/admin-test", methods=["GET"])
@role_required("ADMIN")
def admin_test():
    return jsonify({
        "status": "success",
        "message": "Welcome, Admin!"
    }), 200