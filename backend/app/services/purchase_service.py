from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from uuid import uuid4

from app import db
from app.models.supplier import Supplier
from app.models.item import Item
from app.models.purchase import Purchase
from app.models.purchase_item import PurchaseItem
from app.models.stock_movement import StockMovement
from app.services.inventory_service import record_stock_movement


def to_decimal(value, field_name):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"Invalid {field_name}.")

    if not number.is_finite():
        raise ValueError(f"Invalid {field_name}.")

    return number


def create_purchase(data, user_id):
    supplier_id = data.get("supplier_id")
    items_data = data.get("items")

    if not supplier_id:
        raise ValueError("Supplier ID is required.")

    if not isinstance(items_data, list) or not items_data:
        raise ValueError("At least one purchase item is required.")

    supplier = db.session.get(Supplier, supplier_id)

    if not supplier or not supplier.is_active:
        raise ValueError("Supplier not found or inactive.")

    purchase_date = data.get("purchase_date")

    try:
        if isinstance(purchase_date, str):
            purchase_date = date.fromisoformat(purchase_date)
        elif purchase_date is None:
            purchase_date = date.today()
    except ValueError:
        raise ValueError("Invalid purchase date. Use YYYY-MM-DD.")

    purchase_number = (
        f"PUR-{datetime.now().strftime('%Y%m%d')}-{uuid4().hex[:6].upper()}"
    )

    purchase = Purchase(
        purchase_number=purchase_number,
        supplier_id=supplier_id,
        purchase_date=purchase_date,
        supplier_invoice_number=data.get("supplier_invoice_number"),
        subtotal=Decimal("0"),
        tax_amount=Decimal("0"),
        total_amount=Decimal("0"),
        status="DRAFT",
        notes=data.get("notes"),
        created_by=user_id
    )

    subtotal = Decimal("0")
    total_tax = Decimal("0")

    db.session.add(purchase)
    db.session.flush()

    for entry in items_data:
        item_id = entry.get("item_id")

        item = db.session.get(Item, item_id)

        if not item or not item.is_active:
            raise ValueError(f"Item {item_id} not found or inactive.")

        if item.category not in ("RAW_MATERIAL", "PACKAGING"):
            raise ValueError(
                f"{item.name} is not a raw material or packaging item."
            )

        quantity = to_decimal(entry.get("quantity"), "quantity")
        unit_price = to_decimal(entry.get("unit_price"), "unit price")
        tax_rate = to_decimal(entry.get("tax_rate", 0), "tax rate")

        if quantity <= 0 or unit_price < 0 or tax_rate < 0:
            raise ValueError("Quantity must be positive; price and tax cannot be negative.")

        base_amount = quantity * unit_price
        tax_amount = base_amount * tax_rate / Decimal("100")
        line_total = base_amount + tax_amount

        purchase_item = PurchaseItem(
            purchase_id=purchase.id,
            item_id=item_id,
            quantity=quantity,
            unit_price=unit_price,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            line_total=line_total
        )

        db.session.add(purchase_item)

        subtotal += base_amount
        total_tax += tax_amount

    purchase.subtotal = subtotal
    purchase.tax_amount = total_tax
    purchase.total_amount = subtotal + total_tax

    return purchase


def receive_purchase(purchase_id, user_id):
    purchase = db.session.get(Purchase, purchase_id)

    if not purchase:
        raise ValueError("Purchase not found.")

    if purchase.status != "DRAFT":
        raise ValueError("Only draft purchases can be received.")

    purchase_items = PurchaseItem.query.filter_by(
        purchase_id=purchase.id
    ).all()

    if not purchase_items:
        raise ValueError("Purchase has no items.")

    for purchase_item in purchase_items:
        record_stock_movement(
            item_id=purchase_item.item_id,
            movement_type="IN",
            quantity=purchase_item.quantity,
            reference_type="PURCHASE",
            reference_id=purchase.id,
            notes=f"Stock received for {purchase.purchase_number}",
            created_by=user_id
        )

    purchase.status = "RECEIVED"

    return purchase
