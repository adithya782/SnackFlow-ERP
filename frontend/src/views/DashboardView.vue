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

      <!-- Summary cards -->
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

      <!-- Inventory table -->
      <div class="card border-0 shadow-sm">
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

const loading = ref(true);
const errorMessage = ref("");

const lowStockItems = computed(() =>
  inventory.value.filter((item) => item.low_stock),
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

async function loadDashboard() {
  loading.value = true;
  errorMessage.value = "";

  try {
    const [inventoryResponse, salesResponse, receivablesResponse] =
      await Promise.all([
        api.get("/reports/inventory"),
        api.get("/reports/sales"),
        api.get("/reports/receivables"),
      ]);

    inventory.value = inventoryResponse.data;
    sales.value = salesResponse.data;
    receivables.value = receivablesResponse.data;
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
