<template>
  <div class="container-fluid p-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="fw-bold mb-1">Dashboard</h2>
        <p class="text-muted mb-0">Welcome back, {{ user?.name }}</p>
      </div>

      <button class="btn btn-outline-danger" @click="logout">Logout</button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-success"></div>
      <p class="mt-2 text-muted">Loading dashboard...</p>
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
                <p class="text-muted mb-2">Inventory Items</p>
                <h3 class="fw-bold">{{ inventory.length }}</h3>
                <small class="text-muted">Active items</small>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-xl-3">
            <div class="card dashboard-card border-0 shadow-sm">
              <div class="card-body">
                <p class="text-muted mb-2">Total Sales</p>
                <h3 class="fw-bold text-success">
                  {{ currency(sales.total_sales) }}
                </h3>
                <small class="text-muted">
                  {{ sales.total_invoices || 0 }} issued invoices
                </small>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-xl-3">
            <div class="card dashboard-card border-0 shadow-sm">
              <div class="card-body">
                <p class="text-muted mb-2">Outstanding</p>
                <h3 class="fw-bold text-danger">
                  {{ currency(receivables.total_outstanding) }}
                </h3>
                <small class="text-muted">Pending customer payments</small>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-xl-3">
            <div class="card dashboard-card border-0 shadow-sm">
              <div class="card-body">
                <p class="text-muted mb-2">Low Stock Items</p>
                <h3 class="fw-bold text-warning">{{ lowStockItems.length }}</h3>
                <small class="text-muted">Items needing attention</small>
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
                <p class="text-muted mb-2">Inventory Items</p>
                <h3 class="fw-bold">{{ inventory.length }}</h3>
                <small class="text-muted">Active items</small>
              </div>
            </div>
          </div>

          <div class="col-md-6">
            <div class="card dashboard-card border-0 shadow-sm">
              <div class="card-body">
                <p class="text-muted mb-2">Low Stock Items</p>
                <h3 class="fw-bold text-warning">{{ lowStockItems.length }}</h3>
                <small class="text-muted">Items needing attention</small>
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
                <p class="text-muted mb-2">Total Sales</p>
                <h3 class="fw-bold text-success">
                  {{ currency(sales.total_sales) }}
                </h3>
                <small class="text-muted">
                  {{ sales.total_invoices || 0 }} issued invoices
                </small>
              </div>
            </div>
          </div>

          <div class="col-md-6">
            <div class="card dashboard-card border-0 shadow-sm">
              <div class="card-body">
                <p class="text-muted mb-2">Outstanding</p>
                <h3 class="fw-bold text-danger">
                  {{ currency(receivables.total_outstanding) }}
                </h3>
                <small class="text-muted">Pending customer payments</small>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- SALESMAN DASHBOARD -->
      <template v-else-if="user?.role === 'SALESMAN'">
        <h5 class="fw-bold mb-3">My Sales Overview</h5>

        <div class="row g-3 mb-4">
          <div class="col-md-6 col-xl-3">
            <div class="card dashboard-card border-0 shadow-sm">
              <div class="card-body">
                <p class="text-muted mb-2">Total Orders</p>
                <h3 class="fw-bold">{{ salesmanOrders.length }}</h3>
                <small class="text-muted">Orders created by you</small>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-xl-3">
            <div class="card dashboard-card border-0 shadow-sm">
              <div class="card-body">
                <p class="text-muted mb-2">Pending Approval</p>
                <h3 class="fw-bold text-warning">{{ pendingOrders }}</h3>
                <small class="text-muted">Awaiting Admin review</small>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-xl-3">
            <div class="card dashboard-card border-0 shadow-sm">
              <div class="card-body">
                <p class="text-muted mb-2">Approved Orders</p>
                <h3 class="fw-bold text-success">{{ approvedOrders }}</h3>
                <small class="text-muted">Approved by Admin</small>
              </div>
            </div>
          </div>

          <div class="col-md-6 col-xl-3">
            <div class="card dashboard-card border-0 shadow-sm">
              <div class="card-body">
                <p class="text-muted mb-2">Rejected Orders</p>
                <h3 class="fw-bold text-danger">{{ rejectedOrders }}</h3>
                <small class="text-muted">Rejected by Admin</small>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Sales Orders -->
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h5 class="fw-bold mb-0">My Recent Orders</h5>

              <button
                class="btn btn-sm btn-outline-success"
                @click="loadDashboard"
              >
                Refresh
              </button>
            </div>

            <div class="table-responsive">
              <table class="table table-hover align-middle">
                <thead class="table-light">
                  <tr>
                    <th>Order Number</th>
                    <th>Order Date</th>
                    <th>Amount</th>
                    <th>Status</th>
                  </tr>
                </thead>

                <tbody>
                  <tr v-for="order in recentSalesmanOrders" :key="order.id">
                    <td class="fw-semibold">{{ order.order_number }}</td>
                    <td>{{ order.order_date }}</td>
                    <td>{{ currency(order.total_amount) }}</td>
                    <td>
                      <span class="badge" :class="statusClass(order.status)">
                        {{ order.status }}
                      </span>
                    </td>
                  </tr>

                  <tr v-if="salesmanOrders.length === 0">
                    <td colspan="4" class="text-center text-muted py-4">
                      You haven't created any sales orders yet.
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <small v-if="salesmanOrders.length > 5" class="text-muted">
              Showing the 5 most recent orders. View Sales Orders for the
              complete list.
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
            <h5 class="fw-bold mb-0">Inventory Overview</h5>

            <button
              class="btn btn-sm btn-outline-success"
              @click="loadDashboard"
            >
              Refresh
            </button>
          </div>

          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead class="table-light">
                <tr>
                  <th>Item</th>
                  <th>SKU</th>
                  <th>Category</th>
                  <th>Current Stock</th>
                  <th>Reorder Level</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                <tr v-for="item in inventory" :key="item.item_id">
                  <td class="fw-semibold">{{ item.name }}</td>
                  <td>{{ item.sku }}</td>
                  <td>{{ item.category }}</td>
                  <td>{{ item.current_stock }} {{ item.unit }}</td>
                  <td>{{ item.reorder_level }} {{ item.unit }}</td>
                  <td>
                    <span
                      class="badge"
                      :class="item.low_stock ? 'bg-danger' : 'bg-success'"
                    >
                      {{ item.low_stock ? "Low Stock" : "In Stock" }}
                    </span>
                  </td>
                </tr>

                <tr v-if="inventory.length === 0">
                  <td colspan="6" class="text-center text-muted py-4">
                    No inventory items found.
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
import api from "../services/api";

const router = useRouter();

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

    errorMessage.value =
      error.response?.data?.message ||
      "Unable to load dashboard data. Please try again.";
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
