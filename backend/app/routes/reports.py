
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.services.report_service import (
    get_inventory_report,
    get_sales_report,
    get_production_report,
    get_receivables_report
)
from app.utils.decorators import role_required


reports_bp = Blueprint(
    "reports",
    __name__,
    url_prefix="/api/reports"
)


@reports_bp.route("/inventory", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT", "PRODUCTION")
def inventory_report():
    return jsonify(get_inventory_report()), 200


@reports_bp.route("/sales", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT")
def sales_report():
    return jsonify(get_sales_report()), 200


@reports_bp.route("/production", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT", "PRODUCTION")
def production_report():
    return jsonify(get_production_report()), 200


@reports_bp.route("/receivables", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "ACCOUNTANT")
def receivables_report():
    return jsonify(get_receivables_report()), 200
