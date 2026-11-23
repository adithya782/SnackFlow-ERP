<script setup>
import { ref, computed, onMounted } from "vue";
import api from "../services/api";

const dispatches = ref([]);
const invoices = ref([]);
const customers = ref([]);

const loading = ref(true);
const saving = ref(false);
const error = ref("");
const success = ref("");
const searchQuery = ref("");
const statusFilter = ref("ALL");
const showModal = ref(false);

const form = ref({
  invoice_id: "",
  transporter_name: "",
  vehicle_number: "",
  tracking_number: "",
  notes: "",
});

const customerMap = computed(() =>
  Object.fromEntries(
    customers.value.map((customer) => [customer.id, customer.business_name]),
  ),
);

const invoiceMap = computed(() =>
  Object.fromEntries(invoices.value.map((invoice) => [invoice.id, invoice])),
);

const dispatchedInvoiceIds = computed(
  () => new Set(dispatches.value.map((dispatch) => dispatch.invoice_id)),
);

const availableInvoices = computed(() =>
  invoices.value.filter(
    (invoice) =>
      invoice.status === "ISSUED" &&
      !dispatchedInvoiceIds.value.has(invoice.id),
  ),
);

const filteredDispatches = computed(() =>
  dispatches.value.filter((dispatch) => {
    const invoice = invoiceMap.value[dispatch.invoice_id];
    const customerName = invoice
      ? customerMap.value[invoice.customer_id] || ""
      : "";

    const matchesSearch =
      dispatch.dispatch_number
        .toLowerCase()
        .includes(searchQuery.value.toLowerCase()) ||
      customerName.toLowerCase().includes(searchQuery.value.toLowerCase());

    const matchesStatus =
      statusFilter.value === "ALL" || dispatch.status === statusFilter.value;

    return matchesSearch && matchesStatus;
  }),
);

function formatCurrency(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(Number(value) || 0);
}

function formatDate(value) {
  if (!value) return "-";

  return new Date(value).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function statusClass(status) {
  return status === "DISPATCHED" ? "bg-success" : "bg-warning text-dark";
}

function getInvoiceNumber(invoiceId) {
  return invoiceMap.value[invoiceId]?.invoice_number || `Invoice #${invoiceId}`;
}

function getCustomerName(invoiceId) {
  const invoice = invoiceMap.value[invoiceId];

  if (!invoice) return "-";

  return (
    customerMap.value[invoice.customer_id] || `Customer #${invoice.customer_id}`
  );
}

function resetForm() {
  form.value = {
    invoice_id: "",
    transporter_name: "",
    vehicle_number: "",
    tracking_number: "",
    notes: "",
  };

  error.value = "";
}

function openModal() {
  resetForm();
  showModal.value = true;
}

async function loadData() {
  loading.value = true;
  error.value = "";

  try {
    const [dispatchResponse, invoiceResponse, customerResponse] =
      await Promise.all([
        api.get("/dispatches"),
        api.get("/invoices"),
        api.get("/customers"),
      ]);

    // Dispatch list endpoint returns a direct array.
    dispatches.value = dispatchResponse.data;

    invoices.value = invoiceResponse.data.invoices;
    customers.value = customerResponse.data.customers;
  } catch (err) {
    error.value =
      err.response?.data?.message || "Failed to load dispatch information.";
  } finally {
    loading.value = false;
  }
}

async function createDispatch() {
  error.value = "";
  success.value = "";

  if (!form.value.invoice_id) {
    error.value = "Please select an issued invoice.";
    return;
  }

  saving.value = true;

  try {
    const payload = {
      invoice_id: Number(form.value.invoice_id),
      transporter_name: form.value.transporter_name.trim(),
      vehicle_number: form.value.vehicle_number.trim(),
      tracking_number: form.value.tracking_number.trim(),
      notes: form.value.notes.trim(),
    };

    const response = await api.post("/dispatches", payload);

    success.value = `Dispatch ${response.data.dispatch.dispatch_number} prepared successfully.`;

    showModal.value = false;

    await loadData();
  } catch (err) {
    error.value = err.response?.data?.message || "Failed to create dispatch.";
  } finally {
    saving.value = false;
  }
}

async function markDispatched(dispatch) {
  if (dispatch.status !== "PREPARED") return;

  const confirmed = confirm(
    `Mark ${dispatch.dispatch_number} as dispatched? Finished goods inventory will be deducted.`,
  );

  if (!confirmed) return;

  error.value = "";
  success.value = "";

  try {
    await api.post(`/dispatches/${dispatch.id}/dispatch`);

    success.value = `${dispatch.dispatch_number} dispatched successfully. Inventory updated.`;

    await loadData();
  } catch (err) {
    error.value = err.response?.data?.message || "Failed to dispatch goods.";
  }
}

onMounted(loadData);
</script>

<template>
  <div class="container-fluid py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold mb-1">Dispatches</h3>
        <p class="text-muted mb-0">Prepare and track customer deliveries.</p>
      </div>

      <button class="btn btn-success" @click="openModal">
        + Create Dispatch
      </button>
    </div>

    <div v-if="success" class="alert alert-success alert-dismissible">
      {{ success }}
      <button type="button" class="btn-close" @click="success = ''"></button>
    </div>

    <div v-if="error && !showModal" class="alert alert-danger">
      {{ error }}
    </div>

    <!-- Summary -->
    <div class="row g-3 mb-4">
      <div class="col-md-4">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <p class="text-muted small mb-1">Total Dispatches</p>
            <h4 class="fw-bold mb-0">{{ dispatches.length }}</h4>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <p class="text-muted small mb-1">Prepared</p>
            <h4 class="fw-bold mb-0">
              {{ dispatches.filter((d) => d.status === "PREPARED").length }}
            </h4>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <p class="text-muted small mb-1">Dispatched</p>
            <h4 class="fw-bold mb-0">
              {{ dispatches.filter((d) => d.status === "DISPATCHED").length }}
            </h4>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="card border-0 shadow-sm mb-3">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-8">
            <input
              v-model="searchQuery"
              type="text"
              class="form-control"
              placeholder="Search dispatch number or customer..."
            />
          </div>

          <div class="col-md-4">
            <select v-model="statusFilter" class="form-select">
              <option value="ALL">All Statuses</option>
              <option value="PREPARED">Prepared</option>
              <option value="DISPATCHED">Dispatched</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Dispatch table -->
    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-success"></div>
          <p class="text-muted mt-2">Loading dispatches...</p>
        </div>

        <div
          v-else-if="filteredDispatches.length === 0"
          class="text-center text-muted py-5"
        >
          No dispatches found.
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>Dispatch Number</th>
                <th>Date</th>
                <th>Invoice</th>
                <th>Customer</th>
                <th>Transporter</th>
                <th>Vehicle</th>
                <th>Tracking Number</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="dispatch in filteredDispatches" :key="dispatch.id">
                <td class="fw-semibold">
                  {{ dispatch.dispatch_number }}
                </td>

                <td>{{ formatDate(dispatch.dispatch_date) }}</td>

                <td>
                  {{ getInvoiceNumber(dispatch.invoice_id) }}
                </td>

                <td>
                  {{ getCustomerName(dispatch.invoice_id) }}
                </td>

                <td>{{ dispatch.transporter_name || "-" }}</td>

                <td>{{ dispatch.vehicle_number || "-" }}</td>

                <td>{{ dispatch.tracking_number || "-" }}</td>

                <td>
                  <span class="badge" :class="statusClass(dispatch.status)">
                    {{ dispatch.status }}
                  </span>
                </td>

                <td>
                  <button
                    v-if="dispatch.status === 'PREPARED'"
                    class="btn btn-sm btn-success"
                    @click="markDispatched(dispatch)"
                  >
                    Mark Dispatched
                  </button>

                  <span v-else class="text-muted small"> Completed </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Create dispatch modal -->
    <div v-if="showModal" class="dispatch-overlay">
      <div class="dispatch-modal">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h5 class="fw-bold mb-1">Create Dispatch</h5>
            <p class="text-muted small mb-0">
              Prepare delivery against an issued invoice.
            </p>
          </div>

          <button
            type="button"
            class="btn-close"
            @click="showModal = false"
          ></button>
        </div>

        <form @submit.prevent="createDispatch">
          <div class="mb-3">
            <label class="form-label fw-semibold"> Issued Invoice </label>

            <select v-model="form.invoice_id" class="form-select" required>
              <option value="" disabled>Select issued invoice</option>

              <option
                v-for="invoice in availableInvoices"
                :key="invoice.id"
                :value="invoice.id"
              >
                {{ invoice.invoice_number }} -
                {{ getCustomerName(invoice.id) }} -
                {{ formatCurrency(invoice.total_amount) }}
              </option>
            </select>

            <p
              v-if="availableInvoices.length === 0"
              class="text-muted small mt-2"
            >
              No uninvoiced dispatches are available. Only issued invoices
              without an existing dispatch can be selected.
            </p>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold"> Transporter Name </label>

            <input
              v-model="form.transporter_name"
              type="text"
              class="form-control"
              placeholder="e.g. ABC Transport"
            />
          </div>

          <div class="row g-3 mb-3">
            <div class="col-md-6">
              <label class="form-label fw-semibold"> Vehicle Number </label>

              <input
                v-model="form.vehicle_number"
                type="text"
                class="form-control"
                placeholder="e.g. TN01AB1234"
              />
            </div>

            <div class="col-md-6">
              <label class="form-label fw-semibold"> Tracking Number </label>

              <input
                v-model="form.tracking_number"
                type="text"
                class="form-control"
                placeholder="Optional tracking ID"
              />
            </div>
          </div>

          <div class="mb-4">
            <label class="form-label fw-semibold"> Notes </label>

            <textarea
              v-model="form.notes"
              class="form-control"
              rows="3"
              placeholder="Optional dispatch notes"
            ></textarea>
          </div>

          <div class="alert alert-info small">
            Creating this record prepares the dispatch. Finished goods inventory
            will only be deducted when you mark the dispatch as completed.
          </div>

          <div v-if="error" class="alert alert-danger">
            {{ error }}
          </div>

          <div class="d-flex justify-content-end gap-2">
            <button
              type="button"
              class="btn btn-light"
              @click="showModal = false"
            >
              Cancel
            </button>

            <button
              type="submit"
              class="btn btn-success"
              :disabled="saving || availableInvoices.length === 0"
            >
              {{ saving ? "Creating..." : "Prepare Dispatch" }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dispatch-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  z-index: 1050;
}

.dispatch-modal {
  background: white;
  color: #212529;
  width: 100%;
  max-width: 650px;
  max-height: 92vh;
  overflow-y: auto;
  border-radius: 12px;
  padding: 24px;
}

.dispatch-modal .form-label {
  color: #343a40;
}
</style>
