<script setup>
import { ref, computed, onMounted } from "vue";
import api from "../services/api";

const stockItems = ref([]);
const loading = ref(true);
const error = ref("");
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

const lowStockCount = computed(
  () => stockItems.value.filter((item) => item.low_stock).length,
);

const totalItems = computed(() => stockItems.value.length);

async function fetchStock() {
  loading.value = true;
  error.value = "";

  try {
    const response = await api.get("/inventory/stock");
    console.log("Inventory API response:", response.data);
    stockItems.value = response.data.stock;
  } catch (err) {
    error.value = err.response?.data?.message || "Failed to load inventory.";
  } finally {
    loading.value = false;
  }
}

function formatCategory(category) {
  return category.replaceAll("_", " ");
}

onMounted(fetchStock);
</script>

<template>
  <div class="container-fluid py-3">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold mb-1">Inventory</h3>
        <p class="text-muted mb-0">
          Monitor your stock levels and availability.
        </p>
      </div>

      <button class="btn btn-outline-success" @click="fetchStock">
        ↻ Refresh
      </button>
    </div>

    <!-- Summary cards -->
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

    <!-- Search and filter -->
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

    <!-- Inventory table -->
    <div class="card border-0 shadow-sm">
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
                    :class="item.low_stock ? 'bg-danger' : 'bg-success'"
                  >
                    {{ item.low_stock ? "Low Stock" : "In Stock" }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
