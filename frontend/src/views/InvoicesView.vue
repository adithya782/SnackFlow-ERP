<script setup>
import { ref, computed, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import api from "../services/api";

const { t } = useI18n();

const invoices = ref([]);
const salesOrders = ref([]);
const customers = ref([]);
const items = ref([]);

const loading = ref(true);
const generating = ref(false);
const error = ref("");
const success = ref("");

const searchQuery = ref("");
const statusFilter = ref("ALL");
const selectedOrderId = ref("");

const customerMap = computed(() =>
  Object.fromEntries(
    customers.value.map((customer) => [customer.id, customer.business_name]),
  ),
);

const itemMap = computed(() =>
  Object.fromEntries(items.value.map((item) => [item.id, item.name])),
);

const invoicedOrderIds = computed(
  () => new Set(invoices.value.map((invoice) => invoice.sales_order_id)),
);

const approvedOrders = computed(() =>
  salesOrders.value.filter(
    (order) =>
      order.status === "APPROVED" && !invoicedOrderIds.value.has(order.id),
  ),
);

const filteredInvoices = computed(() =>
  invoices.value.filter((invoice) => {
    const customerName = customerMap.value[invoice.customer_id] || "";

    const matchesSearch =
      invoice.invoice_number
        .toLowerCase()
        .includes(searchQuery.value.toLowerCase()) ||
      customerName.toLowerCase().includes(searchQuery.value.toLowerCase());

    const matchesStatus =
      statusFilter.value === "ALL" || invoice.status === statusFilter.value;

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
  return status === "ISSUED" ? "bg-success" : "bg-warning text-dark";
}

function formatStatus(status) {
  const translations = {
    DRAFT: "invoices.statuses.draft",
    ISSUED: "invoices.statuses.issued",
  };

  return translations[status] ? t(translations[status]) : status;
}

function getCustomerName(customerId) {
  return customerMap.value[customerId] || `Customer #${customerId}`;
}

function getItemName(itemId) {
  return itemMap.value[itemId] || `Item #${itemId}`;
}

async function loadData() {
  loading.value = true;
  error.value = "";

  try {
    const [invoiceResponse, orderResponse, customerResponse, itemResponse] =
      await Promise.all([
        api.get("/invoices"),
        api.get("/sales-orders"),
        api.get("/customers"),
        api.get("/items"),
      ]);

    invoices.value = invoiceResponse.data.invoices;
    salesOrders.value = orderResponse.data.sales_orders;
    customers.value = customerResponse.data.customers;
    items.value = itemResponse.data.items;
  } catch (err) {
    error.value = err.response?.data?.message || t("invoices.loadError");
  } finally {
    loading.value = false;
  }
}

async function generateInvoice() {
  if (!selectedOrderId.value) {
    error.value = t("invoices.selectOrderError");
    return;
  }

  generating.value = true;
  error.value = "";
  success.value = "";

  try {
    const response = await api.post(
      `/invoices/from-sales-order/${selectedOrderId.value}`,
    );

    success.value = t("invoices.generateSuccess", {
      number: response.data.invoice.invoice_number,
    });

    selectedOrderId.value = "";
    await loadData();
  } catch (err) {
    error.value = err.response?.data?.message || t("invoices.generateError");
  } finally {
    generating.value = false;
  }
}

async function issueInvoice(invoice) {
  if (invoice.status !== "DRAFT") return;

  if (
    !confirm(
      t("invoices.confirmIssue", {
        number: invoice.invoice_number,
      }),
    )
  ) {
    return;
  }

  error.value = "";
  success.value = "";

  try {
    await api.post(`/invoices/${invoice.id}/issue`);

    success.value = t("invoices.issueSuccess", {
      number: invoice.invoice_number,
    });

    await loadData();
  } catch (err) {
    error.value = err.response?.data?.message || t("invoices.issueError");
  }
}

async function downloadInvoice(invoice) {
  error.value = "";

  try {
    const response = await api.get(`/invoices/${invoice.id}/pdf`, {
      responseType: "blob",
    });

    const blob = new Blob([response.data], {
      type: "application/pdf",
    });

    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = `${invoice.invoice_number}.pdf`;

    document.body.appendChild(link);
    link.click();
    link.remove();

    window.URL.revokeObjectURL(url);

    success.value = t("invoices.downloadSuccess", {
      number: invoice.invoice_number,
    });
  } catch (err) {
    error.value = t("invoices.downloadError");
  }
}

onMounted(loadData);
</script>

<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold mb-1">{{ t("invoices.title") }}</h3>
        <p class="text-muted mb-0">
          {{ t("invoices.subtitle") }}
        </p>
      </div>

      <button
        class="btn btn-success"
        data-bs-toggle="modal"
        data-bs-target="#generateInvoiceModal"
      >
        + {{ t("invoices.generateInvoice") }}
      </button>
    </div>

    <div v-if="success" class="alert alert-success alert-dismissible">
      {{ success }}
      <button type="button" class="btn-close" @click="success = ''"></button>
    </div>

    <div v-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <!-- Summary cards -->
    <div class="row g-3 mb-4">
      <div class="col-md-4">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <p class="text-muted small mb-1">
              {{ t("invoices.totalInvoices") }}
            </p>
            <h4 class="fw-bold mb-0">{{ invoices.length }}</h4>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <p class="text-muted small mb-1">
              {{ t("invoices.draftInvoices") }}
            </p>
            <h4 class="fw-bold mb-0">
              {{ invoices.filter((i) => i.status === "DRAFT").length }}
            </h4>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <p class="text-muted small mb-1">
              {{ t("invoices.issuedInvoices") }}
            </p>
            <h4 class="fw-bold mb-0">
              {{ invoices.filter((i) => i.status === "ISSUED").length }}
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
              :placeholder="t('invoices.searchPlaceholder')"
            />
          </div>

          <div class="col-md-4">
            <select v-model="statusFilter" class="form-select">
              <option value="ALL">{{ t("invoices.allStatuses") }}</option>
              <option value="DRAFT">{{ t("invoices.statuses.draft") }}</option>
              <option value="ISSUED">
                {{ t("invoices.statuses.issued") }}
              </option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Invoice table -->
    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-success"></div>
          <p class="text-muted mt-2">
            {{ t("invoices.loading") }}
          </p>
        </div>

        <div
          v-else-if="filteredInvoices.length === 0"
          class="text-center text-muted py-5"
        >
          {{ t("invoices.noInvoices") }}
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>{{ t("invoices.invoiceNumber") }}</th>
                <th>{{ t("invoices.date") }}</th>
                <th>{{ t("invoices.customer") }}</th>
                <th>{{ t("invoices.salesOrder") }}</th>
                <th>{{ t("invoices.taxableAmount") }}</th>
                <th>{{ t("invoices.gst") }}</th>
                <th>{{ t("invoices.totalAmount") }}</th>
                <th>{{ t("invoices.status") }}</th>
                <th>{{ t("invoices.actions") }}</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="invoice in filteredInvoices" :key="invoice.id">
                <td class="fw-semibold">
                  {{ invoice.invoice_number }}
                </td>

                <td>{{ formatDate(invoice.invoice_date) }}</td>

                <td>{{ getCustomerName(invoice.customer_id) }}</td>

                <td>#{{ invoice.sales_order_id }}</td>

                <td>{{ formatCurrency(invoice.taxable_amount) }}</td>

                <td>
                  {{ formatCurrency(invoice.total_tax) }}
                  <div class="text-muted small">
                    <span v-if="Number(invoice.igst_amount) > 0">
                      {{ t("invoices.igst") }}
                    </span>
                    <span v-else>
                      {{ t("invoices.cgstSgst") }}
                    </span>
                  </div>
                </td>

                <td class="fw-semibold">
                  {{ formatCurrency(invoice.total_amount) }}
                </td>

                <td>
                  <span class="badge" :class="statusClass(invoice.status)">
                    {{ formatStatus(invoice.status) }}
                  </span>
                </td>

                <td>
                  <div class="d-flex gap-2">
                    <button
                      v-if="invoice.status === 'DRAFT'"
                      class="btn btn-sm btn-success"
                      @click="issueInvoice(invoice)"
                    >
                      {{ t("invoices.issue") }}
                    </button>

                    <button
                      class="btn btn-sm btn-outline-primary"
                      @click="downloadInvoice(invoice)"
                    >
                      {{ t("invoices.pdf") }}
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Generate invoice modal -->
    <div
      class="modal fade"
      id="generateInvoiceModal"
      tabindex="-1"
      aria-hidden="true"
    >
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <div>
              <h5 class="modal-title fw-bold">
                {{ t("invoices.generateInvoice") }}
              </h5>

              <p class="text-muted small mb-0">
                {{ t("invoices.modalSubtitle") }}
              </p>
            </div>

            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
            ></button>
          </div>

          <div class="modal-body">
            <label class="form-label fw-semibold">
              {{ t("invoices.approvedSalesOrder") }}
            </label>

            <select v-model="selectedOrderId" class="form-select">
              <option value="">
                {{ t("invoices.selectSalesOrder") }}
              </option>

              <option
                v-for="order in approvedOrders"
                :key="order.id"
                :value="order.id"
              >
                {{ order.order_number }} -
                {{ getCustomerName(order.customer_id) }} -
                {{ formatCurrency(order.total_amount) }}
              </option>
            </select>

            <div
              v-if="approvedOrders.length === 0"
              class="alert alert-info mt-3 mb-0"
            >
              {{ t("invoices.noApprovedOrders") }}
            </div>

            <p class="text-muted small mt-3 mb-0">
              {{ t("invoices.draftExplanation") }}
            </p>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn btn-light" data-bs-dismiss="modal">
              {{ t("invoices.cancel") }}
            </button>

            <button
              type="button"
              class="btn btn-success"
              :disabled="generating || !selectedOrderId"
              @click="generateInvoice"
            >
              {{
                generating
                  ? t("invoices.generating")
                  : t("invoices.generateInvoice")
              }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="alert alert-warning mt-3 mb-0">
      <strong>{{ t("invoices.demoNotice") }}</strong>
      {{ t("invoices.demoDisclaimer") }}
    </div>
  </div>
</template>
