
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app import db
from app.services.company_service import (
    get_company_settings,
    create_company_settings,
    update_company_settings
)
from app.utils.decorators import role_required


company_bp = Blueprint("company", __name__, url_prefix="/api/company")


def serialize_company(company):
    return {
        "id": company.id,
        "business_name": company.business_name,
        "gstin": company.gstin,
        "address": company.address,
        "city": company.city,
        "state": company.state,
        "pincode": company.pincode,
        "phone": company.phone,
        "email": company.email,
        "created_at": company.created_at.isoformat(),
        "updated_at": company.updated_at.isoformat()
    }


@company_bp.route("", methods=["GET"])
@jwt_required()
def get_company():
    company = get_company_settings()

    if not company:
        return jsonify({"message": "Company details not configured."}), 404

    return jsonify({"company": serialize_company(company)}), 200


@company_bp.route("", methods=["POST"])
@jwt_required()
@role_required("ADMIN")
def create_company():
    data = request.get_json(silent=True) or {}

    try:
        company = create_company_settings(data)
        db.session.commit()

        return jsonify({
            "message": "Company registered successfully.",
            "company": serialize_company(company)
        }), 201

    except ValueError as error:
        db.session.rollback()
        return jsonify({"message": str(error)}), 400

    except Exception:
        db.session.rollback()
        return jsonify({"message": "Unable to register company."}), 500


@company_bp.route("", methods=["PUT"])
@jwt_required()
@role_required("ADMIN")
def update_company():
    company = get_company_settings()

    if not company:
        return jsonify({"message": "Company details not configured."}), 404

    data = request.get_json(silent=True) or {}

    try:
        update_company_settings(company, data)
        db.session.commit()

        return jsonify({
            "message": "Company details updated successfully.",
            "company": serialize_company(company)
        }), 200

    except ValueError as error:
        db.session.rollback()
        return jsonify({"message": str(error)}), 400

    except Exception:
        db.session.rollback()
        return jsonify({"message": "Unable to update company details."}), 500
