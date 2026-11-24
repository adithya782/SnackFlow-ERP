<template>
  <div class="container-fluid p-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold mb-1">{{ $t("dashboard.title") }}</h2>
        <p class="text-muted mb-0">
          {{ $t("dashboard.welcome", { name: user?.name || "" }) }}
        </p>
      </div>
      <button class="btn btn-outline-danger" @click="logout">
        {{ $t("layout.logout") }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-success"></div>
      <p class="mt-2 text-muted">{{ $t("dashboard.loading") }}</p>
    </div>

    <div v-else>
      <!-- Error -->
      <div v-if="errorMessage" class="alert alert-warning">
        {{ errorMessage }}
      </div>

      <!-- ADMIN DASHBOARD -->
      <template v-if="user?.role === 'ADMIN'">
        <div class="row g-3 mb-4">
          <div class="col-md-6 col-xl-3">
            <div class="card dashboard-card border-0 shadow-sm">
              <div class="card-body">
                <p class="text-muted mb-2">
                  {{ $t("dashboard.inventoryItems") }}
                </p>
                <h3 class="fw-bold">{{ inventory.length }}</h3>
                <small class="text-muted">{{
                  $t("dashboard.activeItems")
                }}</small>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-xl-3">
            <div class="card dashboard-card border-0 shadow-sm">
              <div class="card-body">
                <p class="text-muted mb-2">{{ $t("dashboard.totalSales") }}</p>
                <h3 class="fw-bold text-success">
                  {{ currency(sales.total_sales) }}
                </h3>
                <small class="text-muted">
                  {{ sales.total_invoices || 0 }}
                  {{ $t("dashboard.issuedInvoices") }}
                </small>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-xl-3">
            <div class="card dashboard-card border-0 shadow-sm">
              <div class="card-body">
                <p class="text-muted mb-2">{{ $t("dashboard.outstanding") }}</p>
                <h3 class="fw-bold text-danger">
                  {{ currency(receivables.total_outstanding) }}
                </h3>
                <small class="text-muted">{{
                  $t("dashboard.pendingPayments")
                }}</small>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-xl-3">
            <div class="card dashboard-card border-0 shadow-sm">
              <div class="card-body">
                <p class="text-muted mb-2">
                  {{ $t("dashboard.lowStockItems") }}
                </p>
                <h3 class="fw-bold text-warning">{{ lowStockItems.length }}</h3>
                <small class="text-muted">{{
                  $t("dashboard.itemsNeedingAttention")
                }}</small>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- PRODUCTION DASHBOARD -->
      <template v-else-if="user?.role === 'PRODUCTION'">
        <div class="row g-3 mb-4">
          <div class="col-md-6">
            <div class="card dashboard-card border-0 shadow-sm">
              <div class="card-body">
                <p class="text-muted mb-2">
                  {{ $t("dashboard.inventoryItems") }}
                </p>
                <h3 class="fw-bold">{{ inventory.length }}</h3>
                <small class="text-muted">{{
                  $t("dashboard.activeItems")
                }}</small>
              </div>
            </div>
          </div>

          <div class="col-md-6">
            <div class="card dashboard-card border-0 shadow-sm">
              <div class="card-body">
                <p class="text-muted mb-2">
                  {{ $t("dashboard.lowStockItems") }}
                </p>
                <h3 class="fw-bold text-warning">{{ lowStockItems.length }}</h3>
                <small class="text-muted">{{
                  $t("dashboard.itemsNeedingAttention")
                }}</small>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- ACCOUNTANT DASHBOARD -->
      <template v-else-if="user?.role === 'ACCOUNTANT'">
        <div class="row g-3 mb-4">
          <div class="col-md-6">
            <div class="card dashboard-card border-0 shadow-sm">
              <div class="card-body">
                <p class="text-muted mb-2">{{ $t("dashboard.totalSales") }}</p>
                <h3 class="fw-bold text-success">
                  {{ currency(sales.total_sales) }}
                </h3>
                <small class="text-muted">
                  {{ sales.total_invoices || 0 }}
                  {{ $t("dashboard.issuedInvoices") }}
                </small>
              </div>
            </div>
          </div>

          <div class="col-md-6">
            <div class="card dashboard-card border-0 shadow-sm">
              <div class="card-body">
                <p class="text-muted mb-2">{{ $t("dashboard.outstanding") }}</p>
                <h3 class="fw-bold text-danger">
                  {{ currency(receivables.total_outstanding) }}
                </h3>
                <small class="text-muted">{{
                  $t("dashboard.pendingPayments")
                }}</small>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- SALESMAN DASHBOARD -->
      <template v-else-if="user?.role === 'SALESMAN'">
        <h5 class="fw-bold mb-3">{{ $t("dashboard.mySalesOverview") }}</h5>

        <div class="row g-3 mb-4">
          <div class="col-md-6 col-xl-3">
            <div class="card dashboard-card border-0 shadow-sm">
              <div class="card-body">
                <p class="text-muted mb-2">{{ $t("dashboard.totalOrders") }}</p>
                <h3 class="fw-bold">{{ salesmanOrders.length }}</h3>
                <small class="text-muted">{{
                  $t("dashboard.ordersCreatedByYou")
                }}</small>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-xl-3">
            <div class="card dashboard-card border-0 shadow-sm">
              <div class="card-body">
                <p class="text-muted mb-2">
                  {{ $t("dashboard.pendingApproval") }}
                </p>
                <h3 class="fw-bold text-warning">{{ pendingOrders }}</h3>
                <small class="text-muted">{{
                  $t("dashboard.awaitingAdminReview")
                }}</small>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-xl-3">
            <div class="card dashboard-card border-0 shadow-sm">
              <div class="card-body">
                <p class="text-muted mb-2">
                  {{ $t("dashboard.approvedOrders") }}
                </p>
                <h3 class="fw-bold text-success">{{ approvedOrders }}</h3>
                <small class="text-muted">{{
                  $t("dashboard.approvedByAdmin")
                }}</small>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-xl-3">
            <div class="card dashboard-card border-0 shadow-sm">
              <div class="card-body">
                <p class="text-muted mb-2">
                  {{ $t("dashboard.rejectedOrders") }}
                </p>
                <h3 class="fw-bold text-danger">{{ rejectedOrders }}</h3>
                <small class="text-muted">{{
                  $t("dashboard.rejectedByAdmin")
                }}</small>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Sales Orders -->
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="fw-bold mb-0">{{ $t("dashboard.myRecentOrders") }}</h5>
              <button
                class="btn btn-sm btn-outline-success"
                @click="loadDashboard"
              >
                {{ $t("dashboard.refresh") }}
              </button>
            </div>

            <div class="table-responsive">
              <table class="table table-hover align-middle">
                <thead class="table-light">
                  <tr>
                    <th>{{ $t("dashboard.orderNumber") }}</th>
                    <th>{{ $t("dashboard.orderDate") }}</th>
                    <th>{{ $t("dashboard.amount") }}</th>
                    <th>{{ $t("dashboard.status") }}</th>
                  </tr>
                </thead>

                <tbody>
                  <tr v-for="order in recentSalesmanOrders" :key="order.id">
                    <td class="fw-semibold">{{ order.order_number }}</td>
                    <td>{{ order.order_date }}</td>
                    <td>{{ currency(order.total_amount) }}</td>
                    <td>
                      <span class="badge" :class="statusClass(order.status)">
                        {{ translateStatus(order.status) }}
                      </span>
                    </td>
                  </tr>

                  <tr v-if="salesmanOrders.length === 0">
                    <td colspan="4" class="text-center text-muted py-4">
                      {{ $t("dashboard.noSalesOrders") }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <small v-if="salesmanOrders.length > 5" class="text-muted">
              {{ $t("dashboard.showingRecentOrders") }}
            </small>
          </div>
        </div>
      </template>

      <!-- Inventory table: Admin and Production -->
      <div
        v-if="['ADMIN', 'PRODUCTION'].includes(user?.role)"
        class="card border-0 shadow-sm"
      >
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="fw-bold mb-0">
              {{ $t("dashboard.inventoryOverview") }}
            </h5>
            <button
              class="btn btn-sm btn-outline-success"
              @click="loadDashboard"
            >
              {{ $t("dashboard.refresh") }}
            </button>
          </div>

          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead class="table-light">
                <tr>
                  <th>{{ $t("dashboard.item") }}</th>
                  <th>SKU</th>
                  <th>{{ $t("dashboard.category") }}</th>
                  <th>{{ $t("dashboard.currentStock") }}</th>
                  <th>{{ $t("dashboard.reorderLevel") }}</th>
                  <th>{{ $t("dashboard.status") }}</th>
                </tr>
              </thead>

              <tbody>
                <tr v-for="item in inventory" :key="item.item_id">
                  <td class="fw-semibold">{{ item.name }}</td>
                  <td>{{ item.sku }}</td>
                  <td>{{ translateCategory(item.category) }}</td>
                  <td>{{ item.current_stock }} {{ item.unit }}</td>
                  <td>{{ item.reorder_level }} {{ item.unit }}</td>
                  <td>
                    <span
                      class="badge"
                      :class="item.low_stock ? 'bg-danger' : 'bg-success'"
                    >
                      {{
                        item.low_stock
                          ? $t("dashboard.lowStock")
                          : $t("dashboard.inStock")
                      }}
                    </span>
                  </td>
                </tr>

                <tr v-if="inventory.length === 0">
                  <td colspan="6" class="text-center text-muted py-4">
                    {{ $t("dashboard.noInventoryItems") }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import api from "../services/api";

const router = useRouter();
const { t } = useI18n();

const user = ref(JSON.parse(localStorage.getItem("user") || "null"));
const inventory = ref([]);
const sales = ref({});
const receivables = ref({});
const salesmanOrders = ref([]);
const loading = ref(true);
const errorMessage = ref("");

const lowStockItems = computed(() =>
  inventory.value.filter((item) => item.low_stock),
);

const pendingOrders = computed(
  () =>
    salesmanOrders.value.filter((order) => order.status === "SUBMITTED").length,
);

const approvedOrders = computed(
  () =>
    salesmanOrders.value.filter((order) => order.status === "APPROVED").length,
);

const rejectedOrders = computed(
  () =>
    salesmanOrders.value.filter((order) => order.status === "REJECTED").length,
);

const recentSalesmanOrders = computed(() =>
  [...salesmanOrders.value].sort((a, b) => b.id - a.id).slice(0, 5),
);

function currency(value) {
  return (
    "₹" +
    Number(value || 0).toLocaleString("en-IN", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
  );
}

function statusClass(status) {
  const classes = {
    DRAFT: "bg-secondary",
    SUBMITTED: "bg-warning text-dark",
    APPROVED: "bg-success",
    REJECTED: "bg-danger",
    CANCELLED: "bg-secondary",
  };

  return classes[status] || "bg-secondary";
}

function translateStatus(status) {
  const translations = {
    DRAFT: "dashboard.statuses.draft",
    SUBMITTED: "dashboard.statuses.submitted",
    APPROVED: "dashboard.statuses.approved",
    REJECTED: "dashboard.statuses.rejected",
    CANCELLED: "dashboard.statuses.cancelled",
  };

  return translations[status] ? t(translations[status]) : status;
}

function translateCategory(category) {
  const translations = {
    FINISHED_GOOD: "dashboard.categories.finishedGood",
    RAW_MATERIAL: "dashboard.categories.rawMaterial",
    PACKAGING: "dashboard.categories.packaging",
  };

  return translations[category] ? t(translations[category]) : category;
}

async function loadDashboard() {
  loading.value = true;
  errorMessage.value = "";

  inventory.value = [];
  sales.value = {};
  receivables.value = {};
  salesmanOrders.value = [];

  try {
    const role = user.value?.role;

    if (role === "ADMIN") {
      const [inventoryResponse, salesResponse, receivablesResponse] =
        await Promise.all([
          api.get("/reports/inventory"),
          api.get("/reports/sales"),
          api.get("/reports/receivables"),
        ]);

      inventory.value = inventoryResponse.data;
      sales.value = salesResponse.data;
      receivables.value = receivablesResponse.data;
    } else if (role === "PRODUCTION") {
      const inventoryResponse = await api.get("/reports/inventory");
      inventory.value = inventoryResponse.data;
    } else if (role === "ACCOUNTANT") {
      const [salesResponse, receivablesResponse] = await Promise.all([
        api.get("/reports/sales"),
        api.get("/reports/receivables"),
      ]);

      sales.value = salesResponse.data;
      receivables.value = receivablesResponse.data;
    } else if (role === "SALESMAN") {
      const response = await api.get("/sales-orders");
      salesmanOrders.value = response.data.sales_orders || [];
    }
  } catch (error) {
    console.error("Dashboard error:", error);
    errorMessage.value = t("dashboard.loadError");
  } finally {
    loading.value = false;
  }
}

function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("user");
  router.push("/login");
}

onMounted(loadDashboard);
</script>

<style scoped>
.dashboard-card {
  border-radius: 12px;
  transition: transform 0.2s;
}

.dashboard-card:hover {
  transform: translateY(-3px);
}

.table th {
  white-space: nowrap;
}
</style>
