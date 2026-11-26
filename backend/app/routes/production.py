from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db
from app.models.production_run import ProductionRun
from app.models.production_consumption import ProductionConsumption
from app.models.item import Item
from app.services.production_service import (
    create_production_run,
    update_actual_consumption,
    complete_production,
    add_production_overhead,
    get_production_overheads
)
from app.utils.decorators import role_required
from app.models.production_overhead import ProductionOverhead


production_bp = Blueprint(
    "production",
    __name__,
    url_prefix="/api/production"
)


def serialize_production(run):
    consumptions = ProductionConsumption.query.filter_by(
        production_run_id=run.id
    ).all()

    materials = []

    for entry in consumptions:
        item = db.session.get(Item, entry.material_item_id)

        materials.append({
            "material_item_id": entry.material_item_id,
            "material_name": item.name if item else None,
            "unit": item.unit if item else None,
            "planned_quantity": str(entry.planned_quantity),
            "actual_quantity": (
                str(entry.actual_quantity)
                if entry.actual_quantity is not None else None
            ),
            "unit_cost": str(entry.unit_cost)
        })

    return {
        "id": run.id,
        "run_number": run.run_number,
        "bom_id": run.bom_id,
        "planned_output": str(run.planned_output),
        "actual_output": (
            str(run.actual_output)
            if run.actual_output is not None else None
        ),
        "production_date": (
            run.production_date.isoformat()
            if run.production_date else None
        ),
        "status": run.status,
        "notes": run.notes,
        "materials": materials
    }


# GET: List production runs
@production_bp.route("", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "PRODUCTION", "ACCOUNTANT")
def get_production_runs():
    runs = ProductionRun.query.order_by(
        ProductionRun.id.desc()
    ).all()

    return jsonify({
        "status": "success",
        "count": len(runs),
        "production_runs": [
            serialize_production(run) for run in runs
        ]
    }), 200


# GET: Get one production run
@production_bp.route("/<int:run_id>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "PRODUCTION", "ACCOUNTANT")
def get_production_run(run_id):
    run = db.session.get(ProductionRun, run_id)

    if not run:
        return jsonify({
            "status": "error",
            "message": "Production run not found."
        }), 404

    return jsonify({
        "status": "success",
        "production_run": serialize_production(run)
    }), 200


# POST: Create a planned production run
@production_bp.route("/runs", methods=["POST"])
@jwt_required()
@role_required("ADMIN", "PRODUCTION")
def add_production_run():
    data = request.get_json(silent=True) or {}

    try:
        user_id = int(get_jwt_identity())

        run = create_production_run(data, user_id)

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Production run created successfully.",
            "production_run": serialize_production(run)
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
            "message": "An unexpected error occurred."
        }), 500


# PUT: Record actual output and consumption
@production_bp.route("/runs/<int:run_id>/actuals", methods=["PUT"])
@jwt_required()
@role_required("ADMIN", "PRODUCTION")
def update_production_actuals(run_id):
    data = request.get_json(silent=True) or {}

    try:
        run = update_actual_consumption(run_id, data)

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Actual production details saved.",
            "production_run": serialize_production(run)
        }), 200

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
            "message": "An unexpected error occurred."
        }), 500


# POST: Complete production and update stock
@production_bp.route("/runs/<int:run_id>/complete", methods=["POST"])
@jwt_required()
@role_required("ADMIN", "PRODUCTION")
def finish_production(run_id):
    try:
        user_id = int(get_jwt_identity())

        result = complete_production(run_id, user_id)

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Production completed. Inventory updated.",
            "production_run": serialize_production(
                result["production_run"]
            ),
            "total_material_cost": str(
                result["total_material_cost"]
            )
        }), 200

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
            "message": "An unexpected error occurred."
        }), 500


# POST: Add production overhead
@production_bp.route("/runs/<int:run_id>/overheads", methods=["POST"])
@jwt_required()
@role_required("ADMIN", "PRODUCTION", "ACCOUNTANT")
def add_run_overhead(run_id):
    data = request.get_json(silent=True) or {}

    try:
        user_id = int(get_jwt_identity())

        overhead = add_production_overhead(
            run_id, data, user_id
        )

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Production overhead recorded successfully.",
            "overhead": {
                "id": overhead.id,
                "production_run_id": overhead.production_run_id,
                "category": overhead.category,
                "amount": str(overhead.amount),
                "description": overhead.description
            }
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
            "message": "An unexpected error occurred."
        }), 500


# GET: List overheads for a production run
@production_bp.route("/runs/<int:run_id>/overheads", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "PRODUCTION", "ACCOUNTANT")
def list_run_overheads(run_id):
    try:
        overheads = get_production_overheads(run_id)

        return jsonify({
            "status": "success",
            "count": len(overheads),
            "overheads": [
                {
                    "id": entry.id,
                    "production_run_id": entry.production_run_id,
                    "category": entry.category,
                    "amount": str(entry.amount),
                    "description": entry.description
                }
                for entry in overheads
            ]
        }), 200

    except ValueError as error:
        return jsonify({
            "status": "error",
            "message": str(error)
        }), 404
