from app import db


class InvoiceItem(db.Model):
    __tablename__ = "invoice_items"

    id = db.Column(db.Integer, primary_key=True)

    invoice_id = db.Column(db.Integer,db.ForeignKey("invoices.id"),nullable=False)

    item_id = db.Column(db.Integer,db.ForeignKey("items.id"),nullable=False)

    description = db.Column(db.String(200), nullable=False)
    hsn_code = db.Column(db.String(20))

    quantity = db.Column(db.Numeric(12, 3),nullable=False)

    unit_price = db.Column(db.Numeric(12, 2),nullable=False)

    discount_amount = db.Column(db.Numeric(12, 2),nullable=False,default=0)

    taxable_amount = db.Column(db.Numeric(12, 2),nullable=False)

    gst_rate = db.Column(db.Numeric(5, 2),nullable=False,default=0)

    cgst_amount = db.Column(db.Numeric(12, 2),nullable=False,default=0)

    sgst_amount = db.Column(db.Numeric(12, 2),nullable=False,default=0)

    igst_amount = db.Column(db.Numeric(12, 2),nullable=False,default=0)

    line_total = db.Column(db.Numeric(12, 2),nullable=False)

    def __repr__(self):
        return f"<InvoiceItem {self.item_id}>"
