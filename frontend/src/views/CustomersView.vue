<script setup>
import { ref, computed, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import api from "../services/api";

const { t } = useI18n();

const customers = ref([]);
const loading = ref(false);
const saving = ref(false);
const search = ref("");
const showModal = ref(false);
const editingCustomer = ref(null);
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

const filteredCustomers = computed(() => {
  const term = search.value.toLowerCase().trim();

  if (!term) return customers.value;

  return customers.value.filter((customer) =>
    [
      customer.business_name,
      customer.contact_person,
      customer.phone,
      customer.city,
    ].some((value) =>
      String(value || "")
        .toLowerCase()
        .includes(term),
    ),
  );
});

async function loadCustomers() {
  loading.value = true;

  try {
    const response = await api.get("/customers");

    customers.value = Array.isArray(response.data)
      ? response.data
      : response.data.customers || [];
  } catch (error) {
    alert(error.response?.data?.message || t("customers.loadError"));
  } finally {
    loading.value = false;
  }
}

function openAddModal() {
  editingCustomer.value = null;
  form.value = emptyForm();
  formError.value = "";
  showModal.value = true;
}

function openEditModal(customer) {
  editingCustomer.value = customer;

  form.value = {
    business_name: customer.business_name || "",
    contact_person: customer.contact_person || "",
    phone: customer.phone || "",
    email: customer.email || "",
    gstin: customer.gstin || "",
    address: customer.address || "",
    city: customer.city || "",
    state: customer.state || "",
  };

  formError.value = "";
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
  editingCustomer.value = null;
  form.value = emptyForm();
  formError.value = "";
}

async function saveCustomer() {
  saving.value = true;
  formError.value = "";

  try {
    if (editingCustomer.value) {
      await api.put(`/customers/${editingCustomer.value.id}`, form.value);
    } else {
      await api.post("/customers", form.value);
    }

    closeModal();
    await loadCustomers();
  } catch (error) {
    formError.value = error.response?.data?.message || t("customers.saveError");
  } finally {
    saving.value = false;
  }
}

async function toggleStatus(customer) {
  const action = customer.is_active
    ? t("customers.deactivate").toLowerCase()
    : t("customers.activate").toLowerCase();

  if (!confirm(t("customers.confirmStatus", { action }))) {
    return;
  }

  try {
    await api.patch(`/customers/${customer.id}/status`, {
      is_active: !customer.is_active,
    });

    await loadCustomers();
  } catch (error) {
    alert(error.response?.data?.message || t("customers.statusError"));
  }
}

onMounted(loadCustomers);
</script>

<template>
  <div class="customers-page">
    <div
      class="d-flex justify-content-between align-items-center flex-wrap gap-3 mb-4"
    >
      <div>
        <h3 class="fw-bold mb-1">{{ t("customers.title") }}</h3>
        <p class="text-muted mb-0">
          {{ t("customers.subtitle") }}
        </p>
      </div>

      <button class="btn btn-success" @click="openAddModal">
        + {{ t("customers.addCustomer") }}
      </button>
    </div>

    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <div class="row mb-3">
          <div class="col-md-5">
            <input
              v-model="search"
              class="form-control"
              :placeholder="t('customers.searchPlaceholder')"
            />
          </div>
        </div>

        <div v-if="loading" class="text-center py-5 text-muted">
          {{ t("customers.loading") }}
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th>{{ t("customers.businessName") }}</th>
                <th>{{ t("customers.contactPerson") }}</th>
                <th>{{ t("customers.phone") }}</th>
                <th>{{ t("customers.city") }}</th>
                <th>{{ t("customers.status") }}</th>
                <th class="text-end">{{ t("customers.actions") }}</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="customer in filteredCustomers" :key="customer.id">
                <td class="fw-semibold">
                  {{ customer.business_name }}
                </td>

                <td>{{ customer.contact_person || "—" }}</td>
                <td>{{ customer.phone || "—" }}</td>
                <td>{{ customer.city || "—" }}</td>

                <td>
                  <span
                    class="badge"
                    :class="
                      customer.is_active
                        ? 'text-bg-success'
                        : 'text-bg-secondary'
                    "
                  >
                    {{
                      customer.is_active
                        ? t("customers.active")
                        : t("customers.inactive")
                    }}
                  </span>
                </td>

                <td class="text-end">
                  <button
                    class="btn btn-sm btn-outline-primary me-2"
                    @click="openEditModal(customer)"
                  >
                    {{ t("customers.edit") }}
                  </button>

                  <button
                    class="btn btn-sm"
                    :class="
                      customer.is_active
                        ? 'btn-outline-danger'
                        : 'btn-outline-success'
                    "
                    @click="toggleStatus(customer)"
                  >
                    {{
                      customer.is_active
                        ? t("customers.deactivate")
                        : t("customers.activate")
                    }}
                  </button>
                </td>
              </tr>

              <tr v-if="filteredCustomers.length === 0">
                <td colspan="6" class="text-center text-muted py-4">
                  {{ t("customers.noCustomers") }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Add/Edit Customer Modal -->
    <div v-if="showModal" class="modal-backdrop-custom">
      <div class="customer-modal-dialog">
        <div class="modal-content border-0 shadow">
          <div class="modal-header">
            <h5 class="modal-title fw-bold">
              {{
                editingCustomer
                  ? t("customers.editCustomer")
                  : t("customers.addNewCustomer")
              }}
            </h5>

            <button
              type="button"
              class="btn-close"
              @click="closeModal"
            ></button>
          </div>

          <form @submit.prevent="saveCustomer">
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">
                  {{ t("customers.businessName") }} *
                </label>
                <input
                  v-model="form.business_name"
                  class="form-control"
                  required
                />
              </div>

              <div class="mb-3">
                <label class="form-label">
                  {{ t("customers.contactPerson") }}
                </label>
                <input v-model="form.contact_person" class="form-control" />
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">
                    {{ t("customers.phone") }}
                  </label>
                  <input v-model="form.phone" class="form-control" />
                </div>

                <div class="col-md-6 mb-3">
                  <label class="form-label">
                    {{ t("customers.email") }}
                  </label>
                  <input
                    v-model="form.email"
                    type="email"
                    class="form-control"
                  />
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">
                  {{ t("customers.gstin") }}
                </label>
                <input v-model="form.gstin" class="form-control" />
              </div>

              <div class="mb-3">
                <label class="form-label">
                  {{ t("customers.address") }}
                </label>
                <textarea
                  v-model="form.address"
                  class="form-control"
                  rows="2"
                ></textarea>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">
                    {{ t("customers.city") }}
                  </label>
                  <input v-model="form.city" class="form-control" />
                </div>

                <div class="col-md-6 mb-3">
                  <label class="form-label">
                    {{ t("customers.state") }}
                  </label>
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
                {{ t("customers.cancel") }}
              </button>

              <button type="submit" class="btn btn-success" :disabled="saving">
                {{
                  saving ? t("customers.saving") : t("customers.saveCustomer")
                }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.customers-page {
  color: #212529;
}

.customer-modal-dialog {
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
