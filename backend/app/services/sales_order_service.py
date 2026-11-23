from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from uuid import uuid4

from app import db
from app.models.customer import Customer
from app.models.item import Item
from app.models.sales_order import SalesOrder
from app.models.sales_order_item import SalesOrderItem


def to_decimal(value, field_name):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"Invalid {field_name}.")

    if not result.is_finite():
        raise ValueError(f"Invalid {field_name}.")

    return result


def create_sales_order(data, user_id):
    customer_id = data.get("customer_id")
    items_data = data.get("items", [])

    if not customer_id:
        raise ValueError("Customer ID is required.")

    customer = db.session.get(Customer, customer_id)

    if not customer or not customer.is_active:
        raise ValueError("Customer not found or inactive.")

    if not isinstance(items_data, list) or not items_data:
        raise ValueError("At least one order item is required.")

    discount_total = Decimal("0.00")
    subtotal = Decimal("0.00")
    tax_total = Decimal("0.00")

    sales_order = SalesOrder(
        order_number=f"SO-{datetime.now().strftime('%Y%m%d')}-{uuid4().hex[:6].upper()}",
        customer_id=customer.id,
        salesman_id=user_id,
        order_date=date.today(),
        status="DRAFT",
        subtotal=Decimal("0.00"),
        discount_amount=Decimal("0.00"),
        tax_amount=Decimal("0.00"),
        total_amount=Decimal("0.00"),
        notes=data.get("notes")
    )

    db.session.add(sales_order)
    db.session.flush()

    for entry in items_data:
        item_id = entry.get("item_id")

        if not item_id:
            raise ValueError("Item ID is required.")

        item = db.session.get(Item, item_id)

        if (
            not item
            or not item.is_active
            or item.category != "FINISHED_GOOD"
        ):
            raise ValueError(
                f"Invalid or inactive finished product: {item_id}."
            )

        quantity = to_decimal(
            entry.get("quantity"),
            "quantity"
        )

        unit_price = to_decimal(
            entry.get("unit_price"),
            "unit price"
        )

        discount = to_decimal(
            entry.get("discount_amount", 0),
            "discount amount"
        )

        tax_rate = to_decimal(
            entry.get("tax_rate", 0),
            "tax rate"
        )

        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")

        if unit_price < 0:
            raise ValueError("Unit price cannot be negative.")

        if discount < 0:
            raise ValueError("Discount cannot be negative.")

        if tax_rate < 0 or tax_rate > 100:
            raise ValueError("GST rate must be between 0 and 100.")

        gross_amount = quantity * unit_price

        if discount > gross_amount:
            raise ValueError("Discount cannot exceed gross amount.")

        taxable_amount = gross_amount - discount

        line_tax = (
            taxable_amount * tax_rate / Decimal("100")
        ).quantize(Decimal("0.01"))

        line_total = taxable_amount + line_tax

        order_item = SalesOrderItem(
            sales_order_id=sales_order.id,
            item_id=item.id,
            quantity=quantity,
            unit_price=unit_price,
            discount_amount=discount,
            tax_rate=tax_rate,
            tax_amount=line_tax,
            line_total=line_total
        )

        db.session.add(order_item)

        subtotal += gross_amount
        discount_total += discount
        tax_total += line_tax

    sales_order.subtotal = subtotal
    sales_order.discount_amount = discount_total
    sales_order.tax_amount = tax_total
    sales_order.total_amount = (
        subtotal - discount_total + tax_total
    )

    db.session.flush()

    return sales_order


def submit_sales_order(order_id, user_id, user_role):
    sales_order = db.session.get(SalesOrder, order_id)

    if not sales_order:
        raise ValueError("Sales order not found.")

    
    if user_role == "SALESMAN" and sales_order.salesman_id != user_id:
        raise ValueError("You can only submit your own orders.")

    if sales_order.status != "DRAFT":
        raise ValueError("Only draft orders can be submitted.")

    order_items = SalesOrderItem.query.filter_by(
        sales_order_id=sales_order.id
    ).all()

    if not order_items:
        raise ValueError("Cannot submit an empty order.")

    sales_order.status = "SUBMITTED"

    db.session.flush()

    return sales_order

def review_sales_order(order_id, user_id, decision):
    sales_order = db.session.get(SalesOrder, order_id)

    if not sales_order:
        raise ValueError("Sales order not found.")

    if sales_order.status != "SUBMITTED":
        raise ValueError("Only submitted orders can be reviewed.")

    if decision not in ("APPROVED", "REJECTED"):
        raise ValueError("Invalid review decision.")

    sales_order.status = decision
    sales_order.reviewed_by = user_id
    sales_order.reviewed_at = datetime.now(timezone.utc)

    db.session.flush()

    return sales_order

