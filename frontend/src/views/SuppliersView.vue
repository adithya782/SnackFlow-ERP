<script setup>
import { ref, computed, onMounted } from "vue";
import api from "../services/api";

const suppliers = ref([]);
const loading = ref(false);
const saving = ref(false);
const search = ref("");
const showModal = ref(false);
const editingSupplier = ref(null);
const formError = ref("");

const emptyForm = () => ({
  business_name: "",
  contact_person: "",
  phone: "",
  email: "",
  gstin: "",
  address: "",
  city: "",
  state: "",
});

const form = ref(emptyForm());

const filteredSuppliers = computed(() => {
  const term = search.value.toLowerCase().trim();

  if (!term) return suppliers.value;

  return suppliers.value.filter((supplier) =>
    [
      supplier.business_name,
      supplier.contact_person,
      supplier.phone,
      supplier.city,
    ].some((value) =>
      String(value || "")
        .toLowerCase()
        .includes(term),
    ),
  );
});

async function loadSuppliers() {
  loading.value = true;

  try {
    const response = await api.get("/suppliers");
    suppliers.value = Array.isArray(response.data)
      ? response.data
      : response.data.suppliers || [];
  } catch (error) {
    alert(error.response?.data?.message || "Failed to load suppliers");
  } finally {
    loading.value = false;
  }
}

function openAddModal() {
  editingSupplier.value = null;
  form.value = emptyForm();
  formError.value = "";
  showModal.value = true;
}

function openEditModal(supplier) {
  editingSupplier.value = supplier;
  form.value = {
    business_name: supplier.business_name || "",
    contact_person: supplier.contact_person || "",
    phone: supplier.phone || "",
    email: supplier.email || "",
    gstin: supplier.gstin || "",
    address: supplier.address || "",
    city: supplier.city || "",
    state: supplier.state || "",
  };
  formError.value = "";
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
  editingSupplier.value = null;
  form.value = emptyForm();
  formError.value = "";
}

async function saveSupplier() {
  saving.value = true;
  formError.value = "";

  try {
    if (editingSupplier.value) {
      await api.put(`/suppliers/${editingSupplier.value.id}`, form.value);
    } else {
      await api.post("/suppliers", form.value);
    }

    closeModal();
    await loadSuppliers();
  } catch (error) {
    formError.value =
      error.response?.data?.message || "Failed to save supplier";
  } finally {
    saving.value = false;
  }
}

async function toggleStatus(supplier) {
  const action = supplier.is_active ? "deactivate" : "activate";

  if (!confirm(`Are you sure you want to ${action} this supplier?`)) {
    return;
  }

  try {
    await api.patch(`/suppliers/${supplier.id}/status`, {
      is_active: !supplier.is_active,
    });

    await loadSuppliers();
  } catch (error) {
    alert(error.response?.data?.message || "Failed to update status");
  }
}

onMounted(loadSuppliers);
</script>

<template>
  <div class="suppliers-page">
    <div
      class="d-flex justify-content-between align-items-center flex-wrap gap-3 mb-4"
    >
      <div>
        <h3 class="fw-bold mb-1">Suppliers</h3>
        <p class="text-muted mb-0">
          Manage businesses supplying your raw materials
        </p>
      </div>

      <button class="btn btn-success" @click="openAddModal">
        + Add Supplier
      </button>
    </div>

    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <div class="row mb-3">
          <div class="col-md-5">
            <input
              v-model="search"
              class="form-control"
              placeholder="Search by supplier, contact, phone or city..."
            />
          </div>
        </div>

        <div v-if="loading" class="text-center py-5 text-muted">
          Loading suppliers...
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th>Supplier Name</th>
                <th>Contact Person</th>
                <th>Phone</th>
                <th>City</th>
                <th>Status</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="supplier in filteredSuppliers" :key="supplier.id">
                <td class="fw-semibold">{{ supplier.business_name }}</td>
                <td>{{ supplier.contact_person || "—" }}</td>
                <td>{{ supplier.phone || "—" }}</td>
                <td>{{ supplier.city || "—" }}</td>
                <td>
                  <span
                    class="badge"
                    :class="
                      supplier.is_active
                        ? 'text-bg-success'
                        : 'text-bg-secondary'
                    "
                  >
                    {{ supplier.is_active ? "Active" : "Inactive" }}
                  </span>
                </td>
                <td class="text-end">
                  <button
                    class="btn btn-sm btn-outline-primary me-2"
                    @click="openEditModal(supplier)"
                  >
                    Edit
                  </button>

                  <button
                    class="btn btn-sm"
                    :class="
                      supplier.is_active
                        ? 'btn-outline-danger'
                        : 'btn-outline-success'
                    "
                    @click="toggleStatus(supplier)"
                  >
                    {{ supplier.is_active ? "Deactivate" : "Activate" }}
                  </button>
                </td>
              </tr>

              <tr v-if="filteredSuppliers.length === 0">
                <td colspan="6" class="text-center text-muted py-4">
                  No suppliers found.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="showModal" class="modal-backdrop-custom">
      <div class="supplier-modal-dialog">
        <div class="modal-content border-0 shadow">
          <div class="modal-header">
            <h5 class="modal-title fw-bold">
              {{ editingSupplier ? "Edit Supplier" : "Add New Supplier" }}
            </h5>

            <button
              type="button"
              class="btn-close"
              @click="closeModal"
            ></button>
          </div>

          <form @submit.prevent="saveSupplier">
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">Supplier Name *</label>
                <input
                  v-model="form.business_name"
                  class="form-control"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label">Contact Person</label>
                <input v-model="form.contact_person" class="form-control" />
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Phone</label>
                  <input v-model="form.phone" class="form-control" />
                </div>

                <div class="col-md-6 mb-3">
                  <label class="form-label">Email</label>
                  <input
                    v-model="form.email"
                    type="email"
                    class="form-control"
                  />
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">GSTIN</label>
                <input v-model="form.gstin" class="form-control" />
              </div>

              <div class="mb-3">
                <label class="form-label">Address</label>
                <textarea
                  v-model="form.address"
                  class="form-control"
                  rows="2"
                ></textarea>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">City</label>
                  <input v-model="form.city" class="form-control" />
                </div>

                <div class="col-md-6 mb-3">
                  <label class="form-label">State</label>
                  <input v-model="form.state" class="form-control" />
                </div>
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
                {{ saving ? "Saving..." : "Save Supplier" }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.suppliers-page {
  color: #212529;
}

.supplier-modal-dialog {
  width: 100%;
  max-width: 560px;
  margin: auto;
}

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

.modal-content {
  background: #fff;
  color: #212529;
  border: 0;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal-header {
  padding: 22px 26px;
  border-bottom: 1px solid #e9ecef;
}

.modal-title {
  color: #198754;
  font-size: 21px;
}

.modal-body {
  padding: 24px 26px;
  max-height: 65vh;
  overflow-y: auto;
}

.modal-body .form-label {
  display: block;
  color: #343a40 !important;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
}

.modal-body .form-control {
  min-height: 44px;
  padding: 10px 12px;
  border: 1px solid #dce2e8;
  border-radius: 8px;
  background: #fff;
  color: #212529;
  font-size: 14px;
}

.modal-body textarea.form-control {
  min-height: 85px;
}

.modal-body .form-control:focus {
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
