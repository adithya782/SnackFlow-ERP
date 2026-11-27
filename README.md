# 🥨 SnackFlow ERP

![Vue](https://img.shields.io/badge/Vue.js-3-42b883?logo=vuedotjs)
![Flask](https://img.shields.io/badge/Flask-3-black?logo=flask)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169e1?logo=postgresql)
![Render](https://img.shields.io/badge/Deployed-Render-46e3b7?logo=render)

### Manufacturing & Business Management System

A role-based Enterprise Resource Planning (ERP) system designed for small-scale snack manufacturers. SnackFlow streamlines business operations by connecting inventory, procurement, production, sales, invoicing, dispatch, payments, and reporting in one platform.

<p align="center">
  <img src="frontend/1f968.svg" alt="SnackFlow Logo" width="100" />
</p>
<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=22&pause=1000&color=36BCF7&center=true&vCenter=true&width=600&lines=Smart+Manufacturing+Management;Inventory+%7C+Production+%7C+Sales;Welcome+to+SnackFlow+ERP!" />
</p>

---

## 🚀 Live Demo

| Component               | Link                                                                                                       |
| ----------------------- | ---------------------------------------------------------------------------------------------------------- |
| 🌐 Frontend Application | [SnackFlow ERP](https://snackflow-frontend.onrender.com/)                                                  |
| ⚙️ Backend Health Check | [API Status](https://snackflow-erp-jyjh.onrender.com/api/health)                                           |
| 🎥 Demo Video           | [Benchmark test video](https://drive.google.com/file/d/1x8UrUCuf-ZBXvL6W9-ictzx6auWp5lGU/view?usp=sharing) |

> **Note:** The application is hosted on Render's free tier. The backend may take a little time to wake up after inactivity.

---

## 🔑 Demo Access

You can explore SnackFlow ERP using the following demonstration accounts.

| Role                  | Email                      | Password   |
| --------------------- | -------------------------- | ---------- |
| 👑 Admin              | `admin@snackflow.com`      | `password` |
| 🛍️ Sales Executive    | `sales@snackflow.com`      | `password` |
| 🏭 Production Manager | `production@snackflow.com` | `password` |
| 💳 Accountant         | `accounts@snackflow.com`   | `password` |

### 👀 What can you explore?

- **Admin:** User management, company settings, and overall system administration.
- **Sales Executive:** Customer management and sales order processing.
- **Production Manager:** Bills of Materials (BOMs), production planning, and material consumption.
- **Accountant:** Invoice management, payment allocation, receivables, and financial reports.

> ⚠️ **Demo Environment:** These are shared demonstration credentials provided for project evaluation. Please use the accounts only for exploring the application. Avoid entering personal or confidential information.

> 💡 **Note:** The application uses role-based access control, so each account has access only to its permitted modules.

## ✨ Features

### 🌐 Bilingual Language Support

SnackFlow ERP supports both **English and Tamil**, making the system more accessible to administrators, sales staff, and factory floor employees.

Users can switch between languages instantly using the language selector. Their selected preference is saved in the browser and retained across visits.

<p align="center">
  <img src="./language-switch.svg" alt="Language Switch" />
</p>

- English as the default language.
- Tamil language support across the application.
- Instant language switching without reloading the page.
- Language preference persisted using browser local storage.
- Translated navigation, dashboards, forms, tables, and interface messages.
- Business records, product names, numerical values, and calculations remain unchanged.

### 📦 Inventory Management

- Manage raw materials and finished goods.
- Track available stock and stock movements.
- Monitor material consumption and finished product availability.

### 🛒 Procurement

- Manage suppliers and purchase orders.
- Record received materials.
- Automatically update raw material inventory.

### 🏭 Production Management

- Create and manage Bills of Materials (BOMs).
- Plan production based on material requirements.
- Record actual material consumption and production output.
- Track production variance and product costs.
- Record additional production expenses, including labour, gas/power, and other overheads.
- Calculate total production cost and cost per finished unit.

### 💼 Sales Management

- Manage customers and sales orders.
- Submit, approve, or reject orders.
- Track order ownership and status.

### 🧾 Invoicing & Dispatch

- Generate invoices and downloadable PDF documents.
- Manage dispatch records.
- Track finished goods dispatched against sales orders.

### 💰 Payments & Finance

- Record customer payments.
- Allocate payments against invoices.
- Monitor outstanding balances and receivables.

### 📊 Reports & Dashboard

- Sales reports with invoice-wise details and sales summaries.
- Inventory reports with stock levels, reorder levels, and low-stock indicators.
- Production reports with planned output, actual output, material costs, overheads, and cost per unit.
- Receivables reports with payment and outstanding balance details.
- Export Inventory, Sales, and Production reports in Excel (.xlsx), CSV (.csv), and PDF (.pdf) formats.
- Role-specific dashboards.

### 🔐 Authentication & Access Control

- JWT-based authentication.
- Role-based access control (RBAC).
- Access and refresh token handling.
- User management and account activation controls.

---

## 👥 User Roles

| Role          | Responsibilities                                  |
| ------------- | ------------------------------------------------- |
| 👑 Admin      | Complete system management and access control     |
| 🛍️ Salesman   | Customer management and sales order creation      |
| 🏭 Production | Production planning, BOMs, and production records |
| 💳 Accountant | Invoices, payments, and financial reports         |

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    A["👤 User"] --> B["Vue 3 Frontend"]
    B --> C["Flask REST API"]
    C --> D["JWT Authentication"]
    C --> E["Business Logic & Services"]
    E --> F[("PostgreSQL Database")]
    E --> G["PDF Generation"]
    E --> H["Reports & Analytics"]
```

## 🏢 Deployment Model

SnackFlow follows a **Single-Tenant ERP Architecture**, designed for one manufacturing business operating within its own ERP environment.

- **One manufacturing organization:** A single company manages its business operations through SnackFlow.
- **Role-based access:** Multiple employees access the same organization through Admin, Sales, Production, and Accountant roles.
- **Centralized data:** Inventory, procurement, production, customers, sales, and financial records are maintained within the same organizational database.
- **Company-level configuration:** Company details and business settings are managed centrally by the administrator.

> **Scope:** The current implementation supports one manufacturing organization per deployment. It is not designed as a multi-tenant SaaS platform for independently isolated companies.

### 🔄 Core Business Workflow

```mermaid
flowchart TD
    A["🛒 Purchase Raw Materials"] --> B["📦 Update Inventory"]
    B --> C["🏭 Production Planning"]
    C --> D["⚙️ Consume Materials"]
    D --> E["📦 Add Finished Goods"]
    E --> F["🛍️ Create Sales Order"]
    F --> G{"Order Approval"}
    G -->|Approved| H["🧾 Generate Invoice"]
    H --> I["🚚 Dispatch Products"]
    I --> J["💰 Record Payment"]
    J --> K["📊 Update Reports"]
    G -->|Rejected| L["❌ Order Rejected"]
```

### ☁️ Deployment Architecture

```mermaid
flowchart LR
    A["🌐 Browser"] --> B["Render Static Site"]
    B -->|"HTTPS / API Requests"| C["Render Web Service"]
    C --> D[("Render PostgreSQL")]

    style B fill:#dbeafe,stroke:#2563eb,color:#111827
    style C fill:#dcfce7,stroke:#16a34a,color:#111827
    style D fill:#fef3c7,stroke:#d97706,color:#111827
```

---

## 🛠️ Technology Stack

| Category            | Technologies                              |
| ------------------- | ----------------------------------------- |
| Frontend            | Vue 3, JavaScript, HTML, CSS, Bootstrap 5 |
| Backend             | Python, Flask, Flask REST API             |
| Database            | PostgreSQL, SQLAlchemy                    |
| Authentication      | Flask-JWT-Extended                        |
| Database Migrations | Flask-Migrate, Alembic                    |
| PDF Generation      | ReportLab                                 |
| Data Processing     | Pandas, OpenPyXL                          |
| Deployment          | Render                                    |

---

## 📁 Project Structure

```text
SnackFlow-ERP/
│
├── backend/
│   ├── app/
│   │   ├── models/             # Database models
│   │   ├── routes/             # REST API endpoints
│   │   ├── services/           # Business logic
│   │   ├── utils/              # Helpers and utilities
│   │   ├── __init__.py         # Flask application factory
│   │   └── config.py           # Application configuration
│   │
│   ├── migrations/             # Database migration history
│   │   └── versions/
│   ├── requirements.txt
│   ├── run.py                  # Backend entry point
│   ├── seed_admin.py           # Initial admin setup
│   └── seed_admin_render.py    # Cloud admin initialization
│
├── docs/                       # Project documentation
│
├── frontend/
│   ├── public/                 # Static assets and icons
│   ├── src/
│   │   ├── assets/             # Images and frontend assets
│   │   ├── components/         # Reusable Vue components
│   │   ├── layouts/            # Application layouts
│   │   ├── services/           # API integration
│   │   ├── views/              # Application pages
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── router.js           # Vue Router configuration
│   │   └── style.css
│   │
│   ├── .env.development
│   ├── .env.production
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
└── README.md
```

---

## ⚙️ Run Locally

### Prerequisites

- Python 3.11+
- Node.js and npm
- PostgreSQL

### 1. Clone the repository

```bash
git clone https://github.com/adithya782/SnackFlow-ERP.git
cd SnackFlow-ERP
```

### 2. Backend Setup

```bash
cd backend

python -m venv venv
```

Activate the virtual environment:

**Windows**

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file inside `backend/`:

```env
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/snackflow
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

Apply database migrations:

```bash
flask --app run db upgrade
```

Create the initial administrator:

```bash
python seed_admin.py
```

Start the backend:

```bash
python run.py
```

Backend runs at `http://127.0.0.1:5000`.

### 3. Frontend Setup

Open another terminal:

```bash
cd frontend
npm install
```

Create or configure `.env.development`:

```env
VITE_API_BASE_URL=http://127.0.0.1:5000/api
```

Start the frontend:

```bash
npm run dev
```

Open the local URL displayed by Vite.

### 4. Initial Business & Inventory Configuration

After starting the backend and frontend, configure the initial business information, inventory items, opening stock, and Bill of Materials (BOM).

The following configuration is used for the sample SnackFlow manufacturing setup. You can replace these values with your own business information.

#### 4.1 Configure Manufacturer Details

Open PostgreSQL:

```bash
psql -U postgres -d snackflow
```

Check whether company settings already exist:

```sql
SELECT * FROM company_settings;
```

If the table is empty, insert the initial manufacturer details:

```sql
INSERT INTO company_settings (
    business_name,
    gstin,
    address,
    city,
    state,
    pincode,
    phone,
    email
)
VALUES (
    'SnackFlow',
    NULL,
    'Industrial Estate',
    'Chennai',
    'Tamil Nadu',
    '600001',
    '9876543210',
    'admin@snackflow.com'
);
```

Replace the sample address and contact information with your actual business details.

> Note: GSTIN is optional for this demonstration. Use a valid GSTIN when configuring an actual registered business.

#### 4.2 Create Inventory Items

Navigate to **Inventory → Items** and create the following inventory items.

| Item            | SKU           | Category       | Unit    | Opening Quantity |
| --------------- | ------------- | -------------- | ------- | ---------------: |
| Flour           | RM-FLOUR-001  | Raw Material   | kg      |              100 |
| Cooking Oil     | RM-OIL-001    | Raw Material   | L       |               30 |
| Spice Mix       | RM-SPICE-001  | Raw Material   | kg      |                5 |
| Packaging Pouch | PK-POUCH-001  | Packaging      | pcs     |              500 |
| Shipping Carton | PK-CARTON-001 | Packaging      | pcs     |               30 |
| Murukku 200g    | FG-MUR-200    | Finished Goods | packets |               50 |

Sample unit costs:

| Item            | Unit Cost |
| --------------- | --------: |
| Flour           |    ₹42/kg |
| Cooking Oil     |    ₹140/L |
| Spice Mix       |   ₹200/kg |
| Packaging Pouch |  ₹2.50/pc |
| Shipping Carton |    ₹15/pc |

Configure appropriate unit costs and reorder levels while creating the items.

#### 4.3 Record Opening Stock

Creating inventory items does not automatically establish their opening stock balances.

After creating the items, record their opening stock using the inventory functionality.

Use the following quantities:

- Flour: 100 kg
- Cooking Oil: 30 L
- Spice Mix: 5 kg
- Packaging Pouch: 500 pcs
- Shipping Carton: 30 pcs
- Murukku 200g: 50 packets

Opening stock should be recorded as an `IN` inventory movement with the reference type `OPENING`.

To verify inventory balances, execute:

```sql
SELECT
    i.name,
    i.sku,
    i.unit,
    i.current_stock
FROM items i
ORDER BY i.id;
```

> Important: Record opening stock only once for each item. Do not manually update stock balances through SQL after recording opening inventory movements.

#### 4.4 Create the Bill of Materials (BOM)

Navigate to **Production → Bill of Materials** and configure a BOM for the finished product **Murukku 200g**.

Use the following sample production configuration:

| Field            |        Value |
| ---------------- | -----------: |
| Finished Product | Murukku 200g |
| Batch Output     |  200 packets |
| Flour            |        40 kg |
| Cooking Oil      |         10 L |
| Spice Mix        |       1.2 kg |
| Packaging Pouch  |      200 pcs |
| Shipping Carton  |       10 pcs |

Save the BOM and verify that all five components are associated with the finished product.

> The BOM defines standard material consumption for a production batch. Actual consumption should be recorded through the production workflow.

#### 4.5 Configure Product Pricing and GST

Configure the finished product with the following sample values:

| Configuration       |          Value |
| ------------------- | -------------: |
| Product             |   Murukku 200g |
| Selling Price       | ₹50 per packet |
| GST Rate            |             5% |
| Manufacturing State |     Tamil Nadu |

For this demonstration, the GST rate is assumed to be 5%.

#### 4.6 Verify Initial Configuration

Before proceeding with business transactions, verify the following:

- [ ] Manufacturer details are configured.
- [ ] All six inventory items are created.
- [ ] Opening stock is recorded for all items.
- [ ] Inventory balances are correct.
- [ ] Opening stock movements are visible in the inventory ledger.
- [ ] Murukku 200g BOM is created.
- [ ] All five BOM components are configured.
- [ ] Finished product selling price is configured.
- [ ] GST rate is configured.

### 5. Starting with Business Operations

Once the initial configuration is complete, you can start using the ERP system.

Recommended workflow:

1. Create suppliers and retailers.
2. Record purchase orders and purchases.
3. Update inventory through purchase transactions.
4. Record production using the configured BOM.
5. Monitor raw material consumption and finished goods inventory.
6. Create sales orders and invoices.
7. Record customer payments.
8. Allocate payments against outstanding invoices.
9. Generate inventory, production, sales, and financial reports.

**Important:**

- Do not record opening stock multiple times.
- Use the application workflows for inventory changes instead of directly modifying database balances.
- Ensure that master data and BOM configurations are completed before starting production.
- The quantities provided above are sample initial balances for demonstration purposes.

---

## 🔒 Security & Configuration

- Authentication is handled using JWT access and refresh tokens.
- Passwords are handled through the backend authentication service.
- Role-based permissions protect application resources.
- Environment variables are used for sensitive configuration.
- Production and development API URLs are configured separately.

**Never commit `.env` files containing real credentials, database passwords, or secret keys.**

---

## 📌 Project Scope

SnackFlow is developed as a practical ERP solution for a small-scale snack manufacturing business.

The project focuses on connecting everyday business operations, reducing manual record-keeping, improving inventory visibility, and providing a unified view of production and financial activities.

> **Disclaimer:** This is a demonstration ERP application. Invoice documents are intended for demonstration and are not valid GST tax invoices.

---

## 👨‍💻 Developer

Developed as a full-stack ERP project using Vue.js, Flask, and PostgreSQL.

**SnackFlow ERP — From Raw Materials to Revenue.** 🥨

---

⭐ If you find this project interesting, consider giving the repository a star!
