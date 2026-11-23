<script setup>
import { ref, computed, onMounted } from "vue";
import api from "../services/api";

const stockItems = ref([]);
const movements = ref([]);

const loading = ref(true);
const movementLoading = ref(false);
const error = ref("");
const movementError = ref("");

const searchQuery = ref("");
const selectedCategory = ref("ALL");

const categories = ["ALL", "FINISHED_GOOD", "RAW_MATERIAL", "PACKAGING"];

const filteredItems = computed(() => {
  return stockItems.value.filter((item) => {
    const matchesSearch =
      item.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      item.sku.toLowerCase().includes(searchQuery.value.toLowerCase());

    const matchesCategory =
      selectedCategory.value === "ALL" ||
      item.category === selectedCategory.value;

    return matchesSearch && matchesCategory;
  });
});

const isLowStock = (item) => {
  return Number(item.current_stock) <= Number(item.reorder_level);
};

const lowStockCount = computed(
  () => stockItems.value.filter(isLowStock).length,
);

const totalItems = computed(() => stockItems.value.length);

const itemNameMap = computed(() => {
  return Object.fromEntries(
    stockItems.value.map((item) => [item.item_id, item.name]),
  );
});

async function fetchStock() {
  loading.value = true;
  error.value = "";

  try {
    const response = await api.get("/inventory/stock");
    stockItems.value = response.data.stock;
  } catch (err) {
    error.value = err.response?.data?.message || "Failed to load inventory.";
  } finally {
    loading.value = false;
  }
}

async function fetchMovements() {
  movementLoading.value = true;
  movementError.value = "";

  try {
    const response = await api.get("/inventory/movements");
    movements.value = response.data.movements;
  } catch (err) {
    movementError.value =
      err.response?.data?.message || "Failed to load stock movement history.";
  } finally {
    movementLoading.value = false;
  }
}

async function refreshInventory() {
  await Promise.all([fetchStock(), fetchMovements()]);
}

function formatCategory(category) {
  return category.replaceAll("_", " ");
}

function formatDate(value) {
  if (!value) return "-";

  return new Date(value).toLocaleString("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function formatMovementType(type) {
  return type === "IN" ? "Stock In" : "Stock Out";
}

function formatReferenceType(type) {
  return (type || "").replaceAll("_", " ");
}

onMounted(refreshInventory);
</script>

<template>
  <div class="container-fluid py-3">
    <!-- PAGE HEADER -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold mb-1">Inventory</h3>
        <p class="text-muted mb-0">
          Monitor your stock levels and availability.
        </p>
      </div>

      <button
        class="btn btn-outline-success"
        @click="refreshInventory"
        :disabled="loading || movementLoading"
      >
        ↻ Refresh
      </button>
    </div>

    <!-- SUMMARY CARDS -->
    <div class="row g-3 mb-4">
      <div class="col-md-6">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <p class="text-muted mb-1">Total Items</p>
            <h3 class="fw-bold mb-0">{{ totalItems }}</h3>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <p class="text-muted mb-1">Low Stock Items</p>
            <h3 class="fw-bold mb-0 text-danger">{{ lowStockCount }}</h3>
          </div>
        </div>
      </div>
    </div>

    <!-- SEARCH AND FILTER -->
    <div class="card border-0 shadow-sm mb-3">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-7">
            <input
              v-model="searchQuery"
              type="text"
              class="form-control"
              placeholder="Search by item name or SKU..."
            />
          </div>

          <div class="col-md-5">
            <select v-model="selectedCategory" class="form-select">
              <option
                v-for="category in categories"
                :key="category"
                :value="category"
              >
                {{
                  category === "ALL"
                    ? "All Categories"
                    : formatCategory(category)
                }}
              </option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- INVENTORY TABLE -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">Loading inventory...</div>

        <div v-else-if="error" class="alert alert-danger mb-0">
          {{ error }}
        </div>

        <div
          v-else-if="filteredItems.length === 0"
          class="text-center py-5 text-muted"
        >
          No inventory items found.
        </div>

        <div v-else class="table-responsive">
          <table class="table align-middle table-hover">
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
              <tr v-for="item in filteredItems" :key="item.item_id">
                <td class="fw-semibold">{{ item.name }}</td>
                <td>{{ item.sku }}</td>
                <td>{{ formatCategory(item.category) }}</td>

                <td>
                  {{ Number(item.current_stock).toLocaleString("en-IN") }}
                  {{ item.unit }}
                </td>

                <td>
                  {{ Number(item.reorder_level).toLocaleString("en-IN") }}
                  {{ item.unit }}
                </td>

                <td>
                  <span
                    class="badge"
                    :class="isLowStock(item) ? 'bg-danger' : 'bg-success'"
                  >
                    {{ isLowStock(item) ? "Low Stock" : "In Stock" }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- STOCK MOVEMENT HISTORY -->
    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <div
          class="d-flex justify-content-between align-items-center flex-wrap gap-2 mb-3"
        >
          <div>
            <h5 class="fw-bold mb-1">Stock Movement History</h5>
            <p class="text-muted small mb-0">
              Track stock changes and their originating documents.
            </p>
          </div>

          <span class="badge bg-light text-dark border">
            {{ movements.length }} recent movements
          </span>
        </div>

        <div v-if="movementLoading" class="text-center py-4">
          Loading stock movements...
        </div>

        <div v-else-if="movementError" class="alert alert-danger mb-0">
          {{ movementError }}
        </div>

        <div
          v-else-if="movements.length === 0"
          class="text-center text-muted py-4"
        >
          No stock movements recorded yet.
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th>Date & Time</th>
                <th>Item</th>
                <th>Movement</th>
                <th>Quantity</th>
                <th>Source Type</th>
                <th>Source ID</th>
                <th>Notes</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="movement in movements" :key="movement.id">
                <td class="text-nowrap">
                  {{ formatDate(movement.created_at) }}
                </td>

                <td class="fw-semibold">
                  {{
                    itemNameMap[movement.item_id] || `Item #${movement.item_id}`
                  }}
                </td>

                <td>
                  <span
                    class="badge"
                    :class="
                      movement.movement_type === 'IN'
                        ? 'bg-success'
                        : 'bg-danger'
                    "
                  >
                    {{ formatMovementType(movement.movement_type) }}
                  </span>
                </td>

                <td class="fw-semibold">
                  {{ movement.quantity }}
                </td>

                <td>
                  <span class="badge bg-light text-dark border">
                    {{ formatReferenceType(movement.reference_type) }}
                  </span>
                </td>

                <td>
                  <span v-if="movement.reference_id">
                    #{{ movement.reference_id }}
                  </span>
                  <span v-else class="text-muted">-</span>
                </td>

                <td class="movement-notes">
                  {{ movement.notes || "-" }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <p v-if="movements.length > 0" class="text-muted small mb-0 mt-2">
          Showing the latest {{ movements.length }} stock movements.
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.movement-notes {
  min-width: 180px;
  max-width: 260px;
  white-space: normal;
}
</style>
