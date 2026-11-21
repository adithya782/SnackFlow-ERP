from decimal import Decimal, InvalidOperation

from sqlalchemy import case, func

from app import db
from app.models.item import Item
from app.models.stock_movement import StockMovement


def get_item_stock(item_id):
    """Calculate current stock from the stock ledger."""

    result = db.session.query(
        func.coalesce(
            func.sum(
                case(
                    (StockMovement.movement_type == "IN",
                     StockMovement.quantity),
                    else_=-StockMovement.quantity
                )
            ),
            0
        )
    ).filter(
        StockMovement.item_id == item_id
    ).scalar()

    return Decimal(str(result))


def record_stock_movement(
    item_id,
    movement_type,
    quantity,
    reference_type,
    reference_id=None,
    notes=None,
    created_by=None
):
    """Record an IN or OUT stock movement."""

    item = db.session.get(Item, item_id)

    if not item or not item.is_active:
        raise ValueError("Item not found or inactive.")

    movement_type = movement_type.upper()
    reference_type = reference_type.upper()

    if movement_type not in ("IN", "OUT"):
        raise ValueError("Movement type must be IN or OUT.")

    allowed_references = {
        "OPENING", "PURCHASE", "PRODUCTION",
        "DISPATCH", "ADJUSTMENT"
    }

    if reference_type not in allowed_references:
        raise ValueError("Invalid reference type.")

    try:
        quantity = Decimal(str(quantity))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("Invalid quantity.")

    if not quantity.is_finite() or quantity <= 0:
        raise ValueError("Quantity must be a positive number.")

    current_stock = get_item_stock(item_id)

    if movement_type == "OUT" and current_stock < quantity:
        raise ValueError(
            f"Insufficient stock. Available: {current_stock}"
        )

    movement = StockMovement(
        item_id=item_id,
        movement_type=movement_type,
        quantity=quantity,
        reference_type=reference_type,
        reference_id=reference_id,
        notes=notes,
        created_by=created_by
    )

    db.session.add(movement)
    db.session.flush()

    return movement
