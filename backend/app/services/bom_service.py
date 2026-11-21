from decimal import Decimal, InvalidOperation

from app import db
from app.models.item import Item
from app.models.bom import BOM
from app.models.bom_item import BOMItem


def to_decimal(value, field_name):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"Invalid {field_name}.")

    if not number.is_finite():
        raise ValueError(f"Invalid {field_name}.")

    return number


def create_bom(data):
    product_id = data.get("product_id")
    name = data.get("name")
    output_quantity = to_decimal(
        data.get("output_quantity"), "output quantity"
    )
    materials = data.get("items")

    if not product_id:
        raise ValueError("Finished product ID is required.")

    if not name or not name.strip():
        raise ValueError("BOM name is required.")

    if output_quantity <= 0:
        raise ValueError("Output quantity must be positive.")

    if not isinstance(materials, list) or not materials:
        raise ValueError("At least one BOM material is required.")

    product = db.session.get(Item, product_id)

    if not product or not product.is_active:
        raise ValueError("Finished product not found or inactive.")

    if product.category != "FINISHED_GOOD":
        raise ValueError("BOM product must be a finished good.")

    bom = BOM(
        product_id=product_id,
        name=name.strip(),
        output_quantity=output_quantity
    )

    db.session.add(bom)
    db.session.flush()

    seen_materials = set()

    for entry in materials:
        material_id = entry.get("material_item_id")

        if not material_id:
            raise ValueError("Material item ID is required.")

        if material_id in seen_materials:
            raise ValueError("Duplicate material in BOM.")

        seen_materials.add(material_id)

        material = db.session.get(Item, material_id)

        if not material or not material.is_active:
            raise ValueError(
                f"Material item {material_id} not found or inactive."
            )

        if material.category not in ("RAW_MATERIAL", "PACKAGING"):
            raise ValueError(
                f"{material.name} must be a raw material or packaging item."
            )

        quantity = to_decimal(
            entry.get("quantity"), "material quantity"
        )

        if quantity <= 0:
            raise ValueError("Material quantity must be positive.")

        bom_item = BOMItem(
            bom_id=bom.id,
            material_item_id=material_id,
            quantity=quantity
        )

        db.session.add(bom_item)

    return bom
