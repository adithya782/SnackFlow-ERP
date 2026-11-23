import { createRouter, createWebHistory } from "vue-router";

import LandingView from "./views/LandingView.vue";
import LoginView from "./views/LoginView.vue";
import DashboardView from "./views/DashboardView.vue";
import ModulePlaceholderView from "./views/ModulePlaceholderView.vue";
import AppLayout from "./layouts/AppLayout.vue";

import ItemsView from "./views/ItemsView.vue";
import CustomersView from "./views/CustomersView.vue";
import SuppliersView from "./views/SuppliersView.vue";
import InventoryView from "./views/InventoryView.vue";
import PurchasesView from "./views/PurchasesView.vue";
import ProductionView from "./views/ProductionView.vue";
import SalesOrdersView from "./views/SalesOrdersView.vue";
import InvoicesView from "./views/InvoicesView.vue";
import DispatchesView from "./views/DispatchesView.vue";
import PaymentsView from "./views/PaymentsView.vue";
import ReportsView from "./views/ReportsView.vue";
import EmployeesView from "./views/EmployeesView.vue";

const routes = [
  {
    path: "/",
    name: "Landing",
    component: LandingView,
  },
  {
    path: "/login",
    name: "Login",
    component: LoginView,
  },
  {
    path: "/",
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: "dashboard",
        name: "Dashboard",
        component: DashboardView,
      },
      {
        path: "modules/items",
        name: "Items",
        component: ItemsView,
      },
      {
        path: "modules/customers",
        name: "Customers",
        component: CustomersView,
      },
      {
        path: "modules/suppliers",
        name: "Suppliers",
        component: SuppliersView,
      },
      {
        path: "modules/inventory",
        name: "Inventory",
        component: InventoryView,
      },
      {
        path: "modules/purchases",
        name: "Purchases",
        component: PurchasesView,
      },
      {
        path: "modules/production",
        name: "Productions",
        component: ProductionView,
      },
      {
        path: "modules/sales-orders",
        name: "Sales Orders",
        component: SalesOrdersView,
      },
      {
        path: "modules/invoices",
        name: "Invoices",
        component: InvoicesView,
      },
      {
        path: "modules/dispatches",
        name: "Dispatches",
        component: DispatchesView,
      },
      {
        path: "modules/payments",
        name: "Payments",
        component: PaymentsView,
      },
      {
        path: "modules/reports",
        name: "Reports",
        component: ReportsView,
      },
      {
        path: "modules/employees",
        name: "Employees",
        component: EmployeesView,
        meta: { allowedRoles: ["ADMIN"] },
      },
      {
        path: "modules/:module",
        name: "Module",
        component: ModulePlaceholderView,
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  const token = localStorage.getItem("access_token");
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);

  // Authenticated users opening the landing page go to dashboard
  if (to.path === "/" && token) {
    return "/dashboard";
  }

  // Protect internal ERP pages
  if (requiresAuth && !token) {
    return "/login";
  }

  // Prevent authenticated users from returning to login
  if (to.path === "/login" && token) {
    return "/dashboard";
  }

  // Role-based route protection
  const allowedRoles = to.meta.allowedRoles;

  if (allowedRoles) {
    const user = JSON.parse(localStorage.getItem("user") || "null");

    if (!user || !allowedRoles.includes(user.role)) {
      return "/dashboard";
    }
  }
});

export default router;
