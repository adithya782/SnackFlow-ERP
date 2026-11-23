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

| Component               | Link                                                             |
| ----------------------- | ---------------------------------------------------------------- |
| 🌐 Frontend Application | [SnackFlow ERP](https://snackflow-frontend.onrender.com/)        |
| ⚙️ Backend Health Check | [API Status](https://snackflow-erp-jyjh.onrender.com/api/health) |

> **Note:** The application is hosted on Render's free tier. The backend may take a little time to wake up after inactivity.

---

## ✨ Features

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

- Sales reports.
- Inventory reports.
- Production reports.
- Receivables reports.
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
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   └── ...
│   ├── migrations/
│   ├── run.py
│   ├── seed_admin.py
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── router/
│   │   ├── services/
│   │   ├── views/
│   │   └── ...
│   ├── .env.development
│   ├── .env.production
│   └── package.json
│
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
git clone https://github.com/YOUR-GITHUB-USERNAME/SnackFlow-ERP.git
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
