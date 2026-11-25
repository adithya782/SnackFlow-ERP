# SnackFlow ERP – Technical Design Note

**Project:** SnackFlow ERP  
**Domain:** Small-Scale Packaged Snacks Manufacturing  
**Technology Stack:** Vue 3 · Python Flask · PostgreSQL  
**Deployment:** Render

---

## 1. System Architecture

SnackFlow ERP follows a three-tier architecture that separates the presentation layer, application logic, and persistent data storage.

- **Frontend:** Vue 3 provides a responsive, bilingual (English and Tamil) interface. Vue Router manages navigation, and Axios communicates with backend REST APIs.
- **Backend:** Python Flask handles authentication, role-based authorization, business operations, inventory calculations, production workflows, invoicing, and reporting.
- **Database:** PostgreSQL stores users, master data, transactions, stock movements, and financial records. SQLAlchemy provides ORM-based database access, while Flask-Migrate manages schema migrations.
- **Deployment:** The frontend and backend are deployed as separate Render services, with PostgreSQL providing persistent storage.

### Architecture Diagram

```mermaid
flowchart TB
    U["Users<br/>Admin · Salesman · Production · Accountant"]

    subgraph FE["Presentation Layer"]
        V["Vue 3 Frontend"]
        R["Vue Router"]
        I["English / Tamil Interface"]
    end

    subgraph BE["Application Layer"]
        API["Flask REST API"]
        AUTH["JWT Authentication<br/>Role-Based Access Control"]
        BL["Business Logic"]
        REP["Reports and Exports"]
    end

    subgraph DB["Data Layer"]
        ORM["SQLAlchemy ORM"]
        PG[("PostgreSQL Database")]
    end

    U --> V
    V --> R
    V --> I
    V <-->|HTTP / JSON| API
    API --> AUTH
    AUTH --> BL
    BL --> REP
    BL --> ORM
    REP --> ORM
    ORM <--> PG
```

---

## 2. Database Design

The database uses a relational model with primary keys and foreign-key relationships to maintain data consistency.

### Main Entities

| Entity                         | Responsibility                                         |
| ------------------------------ | ------------------------------------------------------ |
| Users                          | Employee accounts, roles, and account status           |
| Customers                      | Customer and GST information                           |
| Suppliers                      | Supplier information                                   |
| Items                          | Finished goods, raw materials, and packaging materials |
| BOMs / BOM Items               | Product recipes and material requirements              |
| Purchases / Purchase Items     | Purchase records and received materials                |
| Production Runs / Consumptions | Planned production, actual consumption, and output     |
| Stock Movements                | Inventory transaction history                          |
| Sales Orders / Order Items     | Customer orders and their products                     |
| Invoices / Invoice Items       | Invoice records and line items                         |
| Dispatches                     | Shipment and dispatch information                      |
| Payments / Payment Allocations | Customer payments and invoice settlements              |
| Audit Logs                     | Relevant system activity records                       |

### Entity Relationship Diagram

```mermaid
erDiagram
    USERS {
        int id PK
        string name
        string email
        string role
        boolean is_active
    }

    CUSTOMERS {
        int id PK
        string business_name
        string gstin
    }

    SUPPLIERS {
        int id PK
        string business_name
        string gstin
    }

    ITEMS {
        int id PK
        string name
        string sku
        string category
        string unit
        decimal reorder_level
    }

    BOMS {
        int id PK
        int finished_item_id FK
    }

    BOM_ITEMS {
        int id PK
        int bom_id FK
        int item_id FK
        decimal quantity
    }

    PURCHASES {
        int id PK
        int supplier_id FK
        int created_by FK
        string status
    }

    PURCHASE_ITEMS {
        int id PK
        int purchase_id FK
        int item_id FK
        decimal quantity
        decimal unit_price
    }

    PRODUCTION_RUNS {
        int id PK
        int bom_id FK
        int created_by FK
        decimal planned_quantity
        decimal actual_quantity
    }

    PRODUCTION_CONSUMPTIONS {
        int id PK
        int production_run_id FK
        int item_id FK
        decimal actual_quantity
    }

    STOCK_MOVEMENTS {
        int id PK
        int item_id FK
        int created_by FK
        string movement_type
        decimal quantity
        string reference_type
        int reference_id
    }

    SALES_ORDERS {
        int id PK
        int customer_id FK
        int created_by FK
        string status
    }

    ORDER_ITEMS {
        int id PK
        int sales_order_id FK
        int item_id FK
        decimal quantity
    }

    INVOICES {
        int id PK
        int sales_order_id FK
        int customer_id FK
        decimal total_amount
        string status
    }

    INVOICE_ITEMS {
        int id PK
        int invoice_id FK
        int item_id FK
        decimal quantity
    }

    DISPATCHES {
        int id PK
        int invoice_id FK
        string status
    }

    PAYMENTS {
        int id PK
        int customer_id FK
        decimal amount
    }

    PAYMENT_ALLOCATIONS {
        int id PK
        int payment_id FK
        int invoice_id FK
        decimal allocated_amount
    }

    USERS ||--o{ PURCHASES : creates
    USERS ||--o{ PRODUCTION_RUNS : creates
    USERS ||--o{ SALES_ORDERS : creates
    USERS ||--o{ STOCK_MOVEMENTS : records

    SUPPLIERS ||--o{ PURCHASES : supplies
    PURCHASES ||--|{ PURCHASE_ITEMS : contains
    ITEMS ||--o{ PURCHASE_ITEMS : purchased_as

    ITEMS ||--o{ BOMS : finished_product
    BOMS ||--|{ BOM_ITEMS : contains
    ITEMS ||--o{ BOM_ITEMS : required_material

    BOMS ||--o{ PRODUCTION_RUNS : used_for
    PRODUCTION_RUNS ||--o{ PRODUCTION_CONSUMPTIONS : records
    ITEMS ||--o{ PRODUCTION_CONSUMPTIONS : consumed

    ITEMS ||--o{ STOCK_MOVEMENTS : tracks

    CUSTOMERS ||--o{ SALES_ORDERS : places
    SALES_ORDERS ||--|{ ORDER_ITEMS : contains
    ITEMS ||--o{ ORDER_ITEMS : ordered_item

    SALES_ORDERS ||--o| INVOICES : generates
    CUSTOMERS ||--o{ INVOICES : billed_to
    INVOICES ||--|{ INVOICE_ITEMS : contains
    ITEMS ||--o{ INVOICE_ITEMS : invoiced_item

    INVOICES ||--o| DISPATCHES : dispatched_as

    CUSTOMERS ||--o{ PAYMENTS : makes
    PAYMENTS ||--o{ PAYMENT_ALLOCATIONS : allocated_through
    INVOICES ||--o{ PAYMENT_ALLOCATIONS : receives
```

_Note: The diagram illustrates the principal business relationships. It is a logical overview rather than a complete representation of every database column._

---

## 3. Inventory and Production Workflow

SnackFlow maintains stock movement records to provide traceability for inventory changes.

### Inventory and Production Flow

```mermaid
flowchart TD
    A["Opening Stock"] --> S["Inventory"]
    B["Purchase Received"] --> S

    S --> C["Production Planning"]
    C --> D["BOM Material Requirements"]
    D --> E["Record Actual Consumption"]
    E --> F["Record Finished Goods Output"]

    F --> S

    S --> G["Approved Sales Order"]
    G --> H["Invoice Generation"]
    H --> I["Dispatch"]
    I --> J["Deduct Finished Goods Stock"]

    S --> K["Stock Movement Ledger"]
    E --> K
    F --> K
    B --> K
    J --> K
```

### Stock Calculation

Inventory movements are recorded as stock-in or stock-out transactions.

**Current Stock = Opening Stock + Total Stock In − Total Stock Out**

Stock movements are recorded for:

- Opening inventory.
- Purchase receipts.
- Raw material consumption.
- Finished goods production.
- Dispatches.
- Inventory adjustments.

Each movement stores the item, movement type, quantity, source transaction reference, timestamp, and recording user where applicable.

The movement history supports traceability between inventory changes and their originating transactions.

### Production Variance

Bills of Materials (BOMs) define the planned quantities of materials required for a production run.

Actual material consumption and finished goods output are recorded separately.

**Material Variance = Actual Consumption − Planned Consumption**

**Yield Variance (%) = (Actual Output − Planned Output) / Planned Output × 100**

This allows production personnel and administrators to identify material overconsumption, underconsumption, and output differences.

---

## 4. Costing Methodology

The costing approach focuses on direct material consumption.

**Direct Material Cost = Σ (Actual Material Quantity × Applicable Unit Cost)**

**Material Cost per Good Unit = Total Direct Material Cost / Good Finished Units Produced**

Purchase records provide material quantity and unit-price information. The applicable material unit cost must follow the valuation method implemented in the application.

Labour, electricity, gas, and other overhead costs should be considered separately when estimating total manufacturing cost. The material-cost calculation alone is not a complete manufacturing cost or statutory inventory valuation.

---

## 5. Security and Design Assumptions

- JWT-based authentication protects application endpoints.
- Role-based access control distinguishes ADMIN, SALESMAN, PRODUCTION, and ACCOUNTANT users.
- Passwords are stored using secure password hashing.
- Customers and suppliers are business records, not application roles.
- The current deployment follows a single-tenant model, supporting one manufacturing organization per deployment.
- English is the default interface language; Tamil is available through the language selector. The selected preference is persisted in browser local storage.
- Business records and database values remain unchanged when switching interface languages.
- Inventory, production, sales, invoicing, dispatch, and payment operations are maintained as separate transactional workflows.

**Project Scope:** SnackFlow ERP connects procurement, inventory, manufacturing, sales, invoicing, dispatch, and payment management in a centralized system designed for a small-scale packaged snacks manufacturer.
