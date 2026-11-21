from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db
from app.models.sales_order import SalesOrder
from app.models.sales_order_item import SalesOrderItem
from app.services.sales_order_service import (
    create_sales_order,
    submit_sales_order,
    review_sales_order
)
from app.utils.decorators import role_required


sales_orders_bp = Blueprint(
    "sales_orders",
    __name__,
    url_prefix="/api/sales-orders"
)

def serialize_sales_order_item(item):
    return {
        "id": item.id,
        "item_id": item.item_id,
        "quantity": str(item.quantity),
        "unit_price": str(item.unit_price),
        "discount_amount": str(item.discount_amount),
        "tax_rate": str(item.tax_rate),
        "tax_amount": str(item.tax_amount),
        "line_total": str(item.line_total)
    }


def serialize_sales_order(order):
    items = SalesOrderItem.query.filter_by(
        sales_order_id=order.id
    ).all()

    return {
        "id": order.id,
        "order_number": order.order_number,
        "customer_id": order.customer_id,
        "salesman_id": order.salesman_id,
        "order_date": order.order_date.isoformat(),
        "status": order.status,
        "subtotal": str(order.subtotal),
        "discount_amount": str(order.discount_amount),
        "tax_amount": str(order.tax_amount),
        "total_amount": str(order.total_amount),
        "notes": order.notes,
        "reviewed_by": order.reviewed_by,
        "reviewed_at": (
            order.reviewed_at.isoformat()
            if order.reviewed_at else None
        ),
        "created_at": (
            order.created_at.isoformat()
            if order.created_at else None
        ),
        "items": [
            serialize_sales_order_item(item)
            for item in items
        ]
    }

@sales_orders_bp.route("", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "SALESMAN", "ACCOUNTANT")
def get_sales_orders():
    orders = SalesOrder.query.order_by(
        SalesOrder.id.desc()
    ).all()

    return jsonify({
        "status": "success",
        "count": len(orders),
        "sales_orders": [
            serialize_sales_order(order)
            for order in orders
        ]
    }), 200

@sales_orders_bp.route("/<int:order_id>", methods=["GET"])
@jwt_required()
@role_required("ADMIN", "SALESMAN", "ACCOUNTANT")
def get_sales_order(order_id):
    order = db.session.get(SalesOrder, order_id)

    if not order:
        return jsonify({
            "status": "error",
            "message": "Sales order not found."
        }), 404

    return jsonify({
        "status": "success",
        "sales_order": serialize_sales_order(order)
    }), 200


@sales_orders_bp.route("", methods=["POST"])
@jwt_required()
@role_required("ADMIN", "SALESMAN")
def add_sales_order():
    data = request.get_json(silent=True) or {}

    try:
        user_id = int(get_jwt_identity())

        order = create_sales_order(data, user_id)

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Sales order created successfully.",
            "sales_order": serialize_sales_order(order)
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
            "message": "An unexpected error occurred while creating the sales order."
        }), 500


@sales_orders_bp.route("/<int:order_id>/submit", methods=["POST"])
@jwt_required()
@role_required("ADMIN", "SALESMAN")
def submit_sales_order_route(order_id):
    try:
        user_id = int(get_jwt_identity())

        order = submit_sales_order(order_id, user_id)

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Sales order submitted successfully.",
            "sales_order": serialize_sales_order(order)
        }), 200

    except ValueError as error:
        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400

    except Exception:
        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred while submitting the sales order."
        }), 500


@sales_orders_bp.route("/<int:order_id>/approve", methods=["POST"])
@jwt_required()
@role_required("ADMIN")
def approve_sales_order_route(order_id):
    try:
        user_id = int(get_jwt_identity())

        order = review_sales_order(
            order_id,
            user_id,
            "APPROVED"
        )

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Sales order approved successfully.",
            "sales_order": serialize_sales_order(order)
        }), 200

    except ValueError as error:
        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400

    except Exception:
        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred while approving the sales order."
        }), 500

@sales_orders_bp.route("/<int:order_id>/reject", methods=["POST"])
@jwt_required()
@role_required("ADMIN")
def reject_sales_order_route(order_id):
    try:
        user_id = int(get_jwt_identity())

        order = review_sales_order(
            order_id,
            user_id,
            "REJECTED"
        )

        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Sales order rejected.",
            "sales_order": serialize_sales_order(order)
        }), 200

    except ValueError as error:
        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": str(error)
        }), 400

    except Exception:
        db.session.rollback()

        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred while rejecting the sales order."
        }), 500
