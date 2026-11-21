import { createRouter, createWebHistory } from "vue-router";

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

const routes = [
  {
    path: "/",
    redirect: "/dashboard",
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
        path: "modules/:module",
        name: "Module",
        component: ModulePlaceholderView,
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

  if (requiresAuth && !token) {
    return "/login";
  }

  if (to.path === "/login" && token) {
    return "/dashboard";
  }
});

export default router;
