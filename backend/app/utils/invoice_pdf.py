from io import BytesIO

from reportlab.lib import colors  # type: ignore
from reportlab.lib.pagesizes import A4   # type: ignore
from reportlab.lib.styles import getSampleStyleSheet   # type: ignore
from reportlab.lib.units import mm # type: ignore 
from reportlab.platypus import ( # type: ignore
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


def generate_invoice_pdf(invoice, company, customer, items):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    styles = getSampleStyleSheet()
    elements = []

    # Company details
    elements.append(Paragraph(
        f"<b>{company.business_name}</b>",
        styles["Title"]
    ))

    elements.append(Paragraph(
        f"{company.address or ''}, "
        f"{company.city or ''}, "
        f"{company.state}",
        styles["Normal"]
    ))

    elements.append(Paragraph(
        f"GSTIN: {company.gstin or 'Not configured'}",
        styles["Normal"]
    ))

    elements.append(Spacer(1, 10))

    # Demo warning
    elements.append(Paragraph(
        "<b>DEMO INVOICE - NOT A VALID GST TAX INVOICE</b>",
        styles["Heading2"]
    ))

    elements.append(Spacer(1, 12))

    # Invoice and customer information
    details = [
        ["Invoice Number", invoice.invoice_number],
        ["Invoice Date", invoice.invoice_date.isoformat()],
        ["Customer", customer.business_name],
        ["Customer GSTIN", customer.gstin or "Not provided"],
        ["Customer Address", customer.address or ""],
        ["Customer State", customer.state or ""]
    ]

    details_table = Table(details, colWidths=[45 * mm, 115 * mm])

    details_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ("PADDING", (0, 0), (-1, -1), 7)
    ]))

    elements.append(details_table)
    elements.append(Spacer(1, 15))

    # Invoice items
    table_data = [[
        "Description",
        "Qty",
        "Rate",
        "Taxable",
        "GST %",
        "Total"
    ]]

    for item in items:
        table_data.append([
            item.description,
            str(item.quantity),
            f"Rs. {item.unit_price}",
            f"Rs. {item.taxable_amount}",
            f"{item.gst_rate}%",
            f"Rs. {item.line_total}"
        ])

    items_table = Table(
        table_data,
        colWidths=[43 * mm, 17 * mm, 25 * mm,
                   25 * mm, 20 * mm, 30 * mm],
        repeatRows=1
    )

    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#263B53")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("PADDING", (0, 0), (-1, -1), 6)
    ]))

    elements.append(items_table)
    elements.append(Spacer(1, 15))

    # Tax summary
    summary = [
        ["Taxable Amount", f"Rs. {invoice.taxable_amount}"],
        ["CGST", f"Rs. {invoice.cgst_amount}"],
        ["SGST", f"Rs. {invoice.sgst_amount}"],
        ["IGST", f"Rs. {invoice.igst_amount}"],
        ["Total Tax", f"Rs. {invoice.total_tax}"],
        ["Grand Total", f"Rs. {invoice.total_amount}"]
    ]

    summary_table = Table(
        summary,
        colWidths=[110 * mm, 50 * mm]
    )

    summary_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("PADDING", (0, 0), (-1, -1), 7),
        ("BACKGROUND", (0, -1), (-1, -1), colors.whitesmoke)
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(
        "This document is generated for demonstration purposes.",
        styles["Normal"]
    ))

    document.build(elements)

    buffer.seek(0)
    return buffer
