
from app.models.item import Item
from app.services.inventory_service import get_item_stock
from app.models.production_run import ProductionRun
from app.models.production_consumption import ProductionConsumption
from decimal import Decimal
from app.models.customer import Customer
from app.models.payment import Payment
from app.models.payment_allocation import PaymentAllocation
from app import db
from app.services.payment_service import get_invoice_outstanding

def get_inventory_report():
    items = Item.query.filter_by(is_active=True).all()

    report = []

    for item in items:
        current_stock = get_item_stock(item.id)

        report.append({
            "item_id": item.id,
            "name": item.name,
            "sku": item.sku,
            "category": item.category,
            "unit": item.unit,
            "current_stock": str(current_stock),
            "reorder_level": str(item.reorder_level),
            "low_stock": current_stock <= item.reorder_level
        })

    return report


from app.models.invoice import Invoice


def get_sales_report():
    invoices = Invoice.query.filter(
        Invoice.status == "ISSUED"
    ).order_by(Invoice.invoice_date.desc()).all()

    total_sales = sum(
        (invoice.total_amount for invoice in invoices),
        start=0
    )

    total_tax = sum(
        (invoice.total_tax for invoice in invoices),
        start=0
    )

    return {
        "total_invoices": len(invoices),
        "total_sales": str(total_sales),
        "total_tax": str(total_tax),
        "invoices": [
            {
                "invoice_id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "customer_id": invoice.customer_id,
                "invoice_date": invoice.invoice_date.isoformat(),
                "total_amount": str(invoice.total_amount),
                "status": invoice.status
            }
            for invoice in invoices
        ]
    }



def get_production_report():
    runs = ProductionRun.query.order_by(
        ProductionRun.production_date.desc()
    ).all()

    report = []

    for run in runs:
        consumptions = ProductionConsumption.query.filter_by(
            production_run_id=run.id
        ).all()

        material_cost = sum(
            (
                Decimal(str(row.actual_quantity or 0))
                * Decimal(str(row.unit_cost or 0))
                for row in consumptions
            ),
            Decimal("0.00")
        )

        cost_per_unit = (
            (material_cost / Decimal(str(run.actual_output))).quantize(
                Decimal("0.01")
            )
            if run.actual_output and run.actual_output > 0
            else Decimal("0.00")
        )

        report.append({
            "production_run_id": run.id,
            "run_number": run.run_number,
            "production_date": run.production_date.isoformat(),
            "status": run.status,
            "planned_output": str(run.planned_output),
            "actual_output": (
                str(run.actual_output)
                if run.actual_output is not None else None
            ),
            "material_cost": str(material_cost),
            "cost_per_unit": str(cost_per_unit)
        })

    return {
        "total_runs": len(runs),
        "completed_runs": sum(
            1 for run in runs if run.status == "COMPLETED"
        ),
        "production_runs": report
    }


def get_receivables_report():
    invoices = Invoice.query.filter_by(
        status="ISSUED"
    ).order_by(Invoice.invoice_date.desc()).all()

    invoice_details = []
    total_invoiced = Decimal("0.00")
    total_paid = Decimal("0.00")

    for invoice in invoices:
        balance = get_invoice_outstanding(invoice.id)

        customer = db.session.get(Customer, invoice.customer_id)

        invoice_total = Decimal(balance["invoice_total"])
        paid_amount = Decimal(balance["paid_amount"])
        outstanding = Decimal(balance["outstanding_amount"])

        total_invoiced += invoice_total
        total_paid += paid_amount

        invoice_details.append({
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "customer_name": customer.business_name if customer else None,
            "invoice_total": str(invoice_total),
            "paid_amount": str(paid_amount),
            "outstanding_amount": str(outstanding),
            "payment_status": (
                "PAID" if outstanding == 0
                else "PARTIALLY_PAID" if paid_amount > 0
                else "UNPAID"
            )
        })

    return {
        "total_invoiced": str(total_invoiced),
        "total_paid": str(total_paid),
        "total_outstanding": str(total_invoiced - total_paid),
        "invoices": invoice_details
    }
