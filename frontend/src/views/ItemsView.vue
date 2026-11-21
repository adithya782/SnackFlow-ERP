<template>
  <div class="container-fluid">
    <!-- Page heading -->
    <div
      class="d-flex justify-content-between align-items-center flex-wrap gap-3 mb-4"
    >
      <div>
        <h2 class="fw-bold mb-1">Items Management</h2>
        <p class="text-muted mb-0">
          Manage finished goods, raw materials and packaging.
        </p>
      </div>

      <button class="btn btn-success" @click="openAddModal">+ Add Item</button>
    </div>

    <!-- Error message -->
    <div v-if="errorMessage" class="alert alert-danger">
      {{ errorMessage }}
    </div>

    <!-- Search and filters -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-7">
            <input
              v-model="search"
              type="text"
              class="form-control"
              placeholder="Search by item name or SKU..."
            />
          </div>

          <div class="col-md-5">
            <select v-model="categoryFilter" class="form-select">
              <option value="">All Categories</option>
              <option value="FINISHED_GOOD">Finished Goods</option>
              <option value="RAW_MATERIAL">Raw Materials</option>
              <option value="PACKAGING">Packaging</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Items table -->
    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-success"></div>
          <p class="text-muted mt-2">Loading items...</p>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th>Item Name</th>
                <th>SKU</th>
                <th>Category</th>
                <th>Unit</th>
                <th>Reorder Level</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="item in filteredItems" :key="item.id">
                <td class="fw-semibold">{{ item.name }}</td>
                <td>{{ item.sku }}</td>
                <td>{{ formatCategory(item.category) }}</td>
                <td>{{ item.unit }}</td>
                <td>{{ item.reorder_level }}</td>

                <td>
                  <span
                    class="badge"
                    :class="item.is_active ? 'bg-success' : 'bg-secondary'"
                  >
                    {{ item.is_active ? "Active" : "Inactive" }}
                  </span>
                </td>

                <td>
                  <button
                    class="btn btn-sm btn-outline-primary me-2"
                    @click="openEditModal(item)"
                  >
                    Edit
                  </button>

                  <button
                    class="btn btn-sm"
                    :class="
                      item.is_active
                        ? 'btn-outline-danger'
                        : 'btn-outline-success'
                    "
                    @click="toggleStatus(item)"
                  >
                    {{ item.is_active ? "Deactivate" : "Activate" }}
                  </button>
                </td>
              </tr>

              <tr v-if="filteredItems.length === 0">
                <td colspan="7" class="text-center text-muted py-4">
                  No items found.
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="text-muted small mt-2">
          Showing {{ filteredItems.length }} of {{ items.length }} items
        </div>
      </div>
    </div>

    <!-- Add/Edit modal -->
    <div v-if="showModal" class="modal-backdrop-custom">
      <div class="item-modal-dialog">
        <div class="modal-content border-0 shadow">
          <div class="modal-header">
            <h5 class="modal-title fw-bold">
              {{ editingItem ? "Edit Item" : "Add New Item" }}
            </h5>

            <button
              type="button"
              class="btn-close"
              @click="closeModal"
            ></button>
          </div>

          <form @submit.prevent="saveItem">
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label text-dark fw-semibold"
                  >Item Name</label
                >
                <input v-model="form.name" class="form-control" required />
              </div>

              <div class="mb-3">
                <label class="form-label text-dark fw-semibold">SKU</label>
                <input v-model="form.sku" class="form-control" required />
              </div>

              <div class="mb-3">
                <label class="form-label text-dark fw-semibold">Category</label>
                <select v-model="form.category" class="form-select" required>
                  <option value="" disabled>Select category</option>
                  <option value="FINISHED_GOOD">Finished Goods</option>
                  <option value="RAW_MATERIAL">Raw Materials</option>
                  <option value="PACKAGING">Packaging</option>
                </select>
              </div>

              <div class="mb-3">
                <label class="form-label text-dark fw-semibold">Unit</label>
                <input
                  v-model="form.unit"
                  class="form-control"
                  placeholder="Example: PACKET, KG, LITRE"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label text-dark fw-semibold"
                  >Reorder Level</label
                >
                <input
                  v-model="form.reorder_level"
                  type="number"
                  min="0"
                  step="0.001"
                  class="form-control"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label text-dark fw-semibold"
                  >Description</label
                >
                <textarea
                  v-model="form.description"
                  class="form-control"
                  rows="2"
                ></textarea>
              </div>

              <div v-if="formError" class="alert alert-danger mb-0">
                {{ formError }}
              </div>
            </div>

            <div class="modal-footer">
              <button
                type="button"
                class="btn btn-outline-secondary"
                @click="closeModal"
              >
                Cancel
              </button>

              <button type="submit" class="btn btn-success" :disabled="saving">
                {{ saving ? "Saving..." : "Save Item" }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import api from "../services/api";

const items = ref([]);
const loading = ref(false);
const saving = ref(false);

const search = ref("");
const categoryFilter = ref("");

const showModal = ref(false);
const editingItem = ref(null);

const errorMessage = ref("");
const formError = ref("");

const emptyForm = () => ({
  name: "",
  sku: "",
  category: "",
  unit: "",
  reorder_level: "0",
  description: "",
});

const form = ref(emptyForm());

const filteredItems = computed(() => {
  return items.value.filter((item) => {
    const searchText = search.value.toLowerCase();

    const matchesSearch =
      item.name.toLowerCase().includes(searchText) ||
      item.sku.toLowerCase().includes(searchText);

    const matchesCategory =
      !categoryFilter.value || item.category === categoryFilter.value;

    return matchesSearch && matchesCategory;
  });
});

function formatCategory(category) {
  return (
    {
      FINISHED_GOOD: "Finished Goods",
      RAW_MATERIAL: "Raw Materials",
      PACKAGING: "Packaging",
    }[category] || category
  );
}

async function loadItems() {
  loading.value = true;
  errorMessage.value = "";

  try {
    const response = await api.get("/items");

    items.value = Array.isArray(response.data)
      ? response.data
      : response.data.items || [];
  } catch (error) {
    console.error(error);
    errorMessage.value =
      error.response?.data?.message || "Unable to load items.";
  } finally {
    loading.value = false;
  }
}

function openAddModal() {
  editingItem.value = null;
  form.value = emptyForm();
  formError.value = "";
  showModal.value = true;
}

function openEditModal(item) {
  editingItem.value = item;

  form.value = {
    name: item.name,
    sku: item.sku,
    category: item.category,
    unit: item.unit,
    reorder_level: item.reorder_level,
    description: item.description || "",
  };

  formError.value = "";
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
  editingItem.value = null;
}

async function saveItem() {
  saving.value = true;
  formError.value = "";

  try {
    const payload = {
      ...form.value,
      reorder_level: Number(form.value.reorder_level),
    };

    if (editingItem.value) {
      await api.put(`/items/${editingItem.value.id}`, payload);
    } else {
      await api.post("/items", payload);
    }

    closeModal();
    await loadItems();
  } catch (error) {
    console.error(error);
    formError.value = error.response?.data?.message || "Unable to save item.";
  } finally {
    saving.value = false;
  }
}

async function toggleStatus(item) {
  const action = item.is_active ? "deactivate" : "activate";

  if (!confirm(`Are you sure you want to ${action} ${item.name}?`)) {
    return;
  }

  errorMessage.value = "";

  try {
    await api.patch(`/items/${item.id}/status`, {
      is_active: !item.is_active,
    });

    await loadItems();
  } catch (error) {
    console.error(error);
    errorMessage.value =
      error.response?.data?.message || "Unable to update item status.";
  }
}

onMounted(loadItems);
</script>

<style scoped>
.modal-backdrop-custom {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  backdrop-filter: blur(3px);
  z-index: 2000;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  overflow-y: auto;
}

.item-modal-dialog {
  width: 100%;
  max-width: 520px;
  margin: auto;
}

.modal-content {
  background: #ffffff;
  color: #212529;
  border: none;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal-header {
  padding: 22px 26px;
  background: #ffffff;
  border-bottom: 1px solid #e9ecef;
}

.modal-title {
  color: #198754;
  font-size: 21px;
}

.modal-body {
  padding: 24px 26px;
  background: #ffffff;
  max-height: 65vh;
  overflow-y: auto;
}

.modal-body .mb-3 {
  margin-bottom: 20px !important;
}

.modal-body .form-label {
  display: block;
  color: #343a40 !important;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
}

.modal-body .form-control,
.modal-body .form-select {
  min-height: 44px;
  padding: 10px 12px;
  border: 1px solid #dce2e8;
  border-radius: 8px;
  background-color: #ffffff;
  color: #212529;
  font-size: 14px;
}

.modal-body textarea.form-control {
  min-height: 85px;
}

.modal-body .form-control:focus,
.modal-body .form-select:focus {
  border-color: #198754;
  box-shadow: 0 0 0 3px rgba(25, 135, 84, 0.12);
}

.modal-footer {
  padding: 16px 26px;
  border-top: 1px solid #e9ecef;
  background: #fafbfc;
  gap: 10px;
}

.modal-footer .btn {
  padding: 9px 18px;
  border-radius: 8px;
  font-weight: 500;
}

.table th {
  white-space: nowrap;
  font-size: 13px;
}

.table td {
  font-size: 14px;
}

@media (max-width: 576px) {
  .modal-backdrop-custom {
    padding: 10px;
  }

  .modal-header,
  .modal-body {
    padding: 18px;
  }

  .modal-footer {
    padding: 14px 18px;
  }
}
</style>
