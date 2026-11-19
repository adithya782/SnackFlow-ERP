# SnackFlow ERP

## About the Project

An integrated Order-to-Audit ERP system for a small-scale packaged snacks manufacturing business.

The system aims to connect sales, production, inventory, billing and financial reporting in one platform, replacing disconnected manual records and spreadsheets.

## Problem Statement

Develop an ERP solution that manages the complete business workflow, starting from salesman order placement and ending with monthly auditor reports.

The system should connect:

- **Sales:** Orders, approval, GST invoicing, dispatch and payments.
- **Production:** Raw material consumption, production output, wastage and costing.
- **Inventory:** Raw materials, packaging materials and finished goods.
- **Reporting:** Sales, GST, stock, production and financial reports.

## MVP – Minimum Viable Product

The first version will focus on the following essential features:

- [ ] Role-based login (Admin, Salesman, Production Supervisor, Accountant)
- [ ] Customer, product and raw material management
- [ ] Bill of Materials (BOM)
- [ ] Purchase and inventory management
- [ ] Production entry with planned vs actual variance
- [ ] Automatic raw material and finished goods stock updates
- [ ] Mobile-friendly salesman order placement
- [ ] Admin order verification and approval
- [ ] GST invoice generation (PDF)
- [ ] Dispatch and payment tracking
- [ ] Production costing
- [ ] Sales and inventory reports
- [ ] CSV/Excel exports

## Technology Stack

- **Frontend:** Vue 3, Vite, Bootstrap 5
- **Backend:** Python, Flask REST API
- **Database:** PostgreSQL
- **ORM:** Flask-SQLAlchemy
- **Version Control:** Git and GitHub

## Development Checkpoints

| Date   | Milestone                      | Status |
| ------ | ------------------------------ | ------ |
| Nov 17 | Project setup and architecture | ✅     |
| Nov 18 | Database                       | ✅     |

**Status legend:** ⬜ Not started · 🟡 In progress · ✅ Completed

## Additional Notes

- Maintain accurate stock through a transaction-based inventory ledger.
- Use database transactions for production and dispatch operations.
- Avoid deleting posted financial records; use appropriate correction entries.
- Prioritize correctness and a complete end-to-end workflow over unnecessary features.
- Update this README after completing each development checkpoint.

## Repository Structure

```text
SnackFlow-ERP/
├── backend/
├── frontend/
├── docs/
└── README.md
```
