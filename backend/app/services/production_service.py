from decimal import Decimal, InvalidOperation
from datetime import date, datetime
from uuid import uuid4
from sqlalchemy import func

from app.models.purchase import Purchase
from app.models.purchase_item import PurchaseItem

from app import db
from app.models.bom import BOM
from app.models.bom_item import BOMItem
from app.models.item import Item
from app.models.production_run import ProductionRun
from app.models.production_consumption import ProductionConsumption
from app.services.inventory_service import (
    get_item_stock,
    record_stock_movement
)
from app.models.production_overhead import ProductionOverhead

def to_decimal(value, field_name):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"Invalid {field_name}.")

    if not number.is_finite():
        raise ValueError(f"Invalid {field_name}.")

    return number


def create_production_run(data, user_id):
    bom_id = data.get("bom_id")
    planned_output = to_decimal(
        data.get("planned_output"), "planned output"
    )

    if not bom_id:
        raise ValueError("BOM ID is required.")

    if planned_output <= 0:
        raise ValueError("Planned output must be positive.")

    bom = db.session.get(BOM, bom_id)

    if not bom:
        raise ValueError("BOM not found.")

    product = db.session.get(Item, bom.product_id)

    if not product or not product.is_active:
        raise ValueError("Finished product is unavailable.")

    bom_items = BOMItem.query.filter_by(bom_id=bom.id).all()

    if not bom_items:
        raise ValueError("BOM has no materials.")

    production_run = ProductionRun(
    run_number=f"PRD-{datetime.now().strftime('%Y%m%d')}-{uuid4().hex[:6].upper()}",
    bom_id=bom.id,
    planned_output=planned_output,
    actual_output=None,
    production_date=date.today(),
    status="PLANNED",
    created_by=user_id
)

    db.session.add(production_run)
    db.session.flush()

    scale = planned_output / Decimal(str(bom.output_quantity))

    for bom_item in bom_items:
        planned_quantity = Decimal(str(bom_item.quantity)) * scale

        consumption = ProductionConsumption(
            production_run_id=production_run.id,
            material_item_id=bom_item.material_item_id,
            planned_quantity=planned_quantity,
            actual_quantity=None,
            unit_cost=Decimal("0")
        )

        db.session.add(consumption)

    return production_run


def update_actual_consumption(production_run_id, data):
    production_run = db.session.get(
        ProductionRun, production_run_id
    )

    if not production_run:
        raise ValueError("Production run not found.")

    if production_run.status != "PLANNED":
        raise ValueError("Only planned production runs can be updated.")

    actual_output = to_decimal(
        data.get("actual_output"), "actual output"
    )

    if actual_output <= 0:
        raise ValueError("Actual output must be positive.")

    actual_items = data.get("consumptions")

    if not isinstance(actual_items, list) or not actual_items:
        raise ValueError("Actual material consumptions are required.")

    consumptions = ProductionConsumption.query.filter_by(
        production_run_id=production_run.id
    ).all()

    consumption_map = {
        entry.material_item_id: entry for entry in consumptions
    }

    received_ids = set()

    for entry in actual_items:
        material_id = entry.get("material_item_id")

        if material_id in received_ids:
            raise ValueError("Duplicate material consumption.")

        received_ids.add(material_id)

        consumption = consumption_map.get(material_id)

        if not consumption:
            raise ValueError(
                f"Material {material_id} is not part of this BOM."
            )

        actual_quantity = to_decimal(
            entry.get("actual_quantity"), "actual quantity"
        )

        if actual_quantity <= 0:
            raise ValueError("Actual quantity must be positive.")

        consumption.actual_quantity = actual_quantity

    if received_ids != set(consumption_map.keys()):
        raise ValueError("Provide actual consumption for every BOM material.")

    production_run.actual_output = actual_output
    production_run.status = "IN_PROGRESS"

    return production_run


def get_average_purchase_cost(item_id):
    result = db.session.query(
        func.sum(PurchaseItem.quantity * PurchaseItem.unit_price),
        func.sum(PurchaseItem.quantity)
    ).join(
        Purchase,
        Purchase.id == PurchaseItem.purchase_id
    ).filter(
        PurchaseItem.item_id == item_id,
        Purchase.status == "RECEIVED"
    ).one()

    total_value, total_quantity = result

    if not total_quantity or total_quantity <= 0:
        raise ValueError(
            f"No received purchase cost found for item {item_id}."
        )

    return (
        Decimal(str(total_value)) /
        Decimal(str(total_quantity))
    )


def complete_production(production_run_id, user_id):
    production_run = db.session.get(
        ProductionRun, production_run_id
    )

    if not production_run:
        raise ValueError("Production run not found.")

    if production_run.status != "IN_PROGRESS":
        raise ValueError("Production run must be IN_PROGRESS.")

    consumptions = ProductionConsumption.query.filter_by(
        production_run_id=production_run.id
    ).all()

    if not consumptions:
        raise ValueError("Production run has no material consumptions.")

    total_material_cost = Decimal("0")

    # Validate all materials before creating any movements.
    for consumption in consumptions:
        if consumption.actual_quantity is None:
            raise ValueError("Actual consumption is missing.")

        stock = get_item_stock(consumption.material_item_id)

        if stock < consumption.actual_quantity:
            material = db.session.get(
                Item, consumption.material_item_id
            )
            raise ValueError(
                f"Insufficient stock for {material.name}. "
                f"Available: {stock}, Required: {consumption.actual_quantity}"
            )

    # Consume materials and calculate cost.
    for consumption in consumptions:
        material_stock = get_item_stock(
            consumption.material_item_id
        )

        # Calculate weighted average purchase cost.
        unit_cost = Decimal(str(consumption.unit_cost or 0))

        if unit_cost <= 0:
            unit_cost = get_average_purchase_cost(
                consumption.material_item_id
            )

        consumption.unit_cost = unit_cost

        record_stock_movement(
            item_id=consumption.material_item_id,
            movement_type="OUT",
            quantity=consumption.actual_quantity,
            reference_type="PRODUCTION",
            reference_id=production_run.id,
            notes=f"Consumed for {production_run.run_number}",
            created_by=user_id
        )

        total_material_cost += (
            consumption.actual_quantity * unit_cost
        )

    bom = db.session.get(BOM, production_run.bom_id)

    record_stock_movement(
        item_id=bom.product_id,
        movement_type="IN",
        quantity=production_run.actual_output,
        reference_type="PRODUCTION",
        reference_id=production_run.id,
        notes=f"Produced in {production_run.run_number}",
        created_by=user_id
    )

    production_run.status = "COMPLETED"

    return {
        "production_run": production_run,
        "total_material_cost": total_material_cost
    }


def add_production_overhead(production_run_id, data, user_id):
    production_run = db.session.get(
        ProductionRun, production_run_id
    )

    if not production_run:
        raise ValueError("Production run not found.")

    if production_run.status != "COMPLETED":
        raise ValueError(
            "Overheads can only be recorded for completed production runs."
        )

    category = str(data.get("category", "")).strip().upper()

    allowed_categories = {"LABOUR", "GAS_POWER", "OTHER"}

    if category not in allowed_categories:
        raise ValueError(
            "Invalid category. Use LABOUR, GAS_POWER or OTHER."
        )

    amount = to_decimal(data.get("amount"), "overhead amount")

    if amount <= 0:
        raise ValueError("Overhead amount must be positive.")

    overhead = ProductionOverhead(
        production_run_id=production_run.id,
        category=category,
        amount=amount,
        description=data.get("description"),
        created_by=user_id
    )

    db.session.add(overhead)

    return overhead


def get_production_overheads(production_run_id):
    production_run = db.session.get(
        ProductionRun, production_run_id
    )

    if not production_run:
        raise ValueError("Production run not found.")

    return ProductionOverhead.query.filter_by(
        production_run_id=production_run_id
    ).order_by(ProductionOverhead.id.asc()).all()
