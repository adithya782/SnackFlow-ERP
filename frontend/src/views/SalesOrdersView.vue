<script setup>
import { ref, computed, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import api from "../services/api";

const { t } = useI18n();

const salesOrders = ref([]);
const customers = ref([]);
const items = ref([]);
const loading = ref(true);
const saving = ref(false);
const showModal = ref(false);
const error = ref("");
const success = ref("");
const searchQuery = ref("");
const statusFilter = ref("ALL");

const form = ref({
  customer_id: "",
  notes: "",
  items: [
    {
      item_id: "",
      quantity: 1,
      unit_price: 0,
      discount_amount: 0,
      tax_rate: 5,
    },
  ],
});

// Customer lookup
const customerMap = computed(() => {
  return Object.fromEntries(
    customers.value.map((customer) => [customer.id, customer.business_name]),
  );
});

// Item lookup
const itemMap = computed(() => {
  return Object.fromEntries(items.value.map((item) => [item.id, item.name]));
});

// Order filtering
const filteredOrders = computed(() => {
  return salesOrders.value.filter((order) => {
    const customerName = customerMap.value[order.customer_id] || "";

    const matchesSearch =
      order.order_number
        .toLowerCase()
        .includes(searchQuery.value.toLowerCase()) ||
      customerName.toLowerCase().includes(searchQuery.value.toLowerCase());

    const matchesStatus =
      statusFilter.value === "ALL" || order.status === statusFilter.value;

    return matchesSearch && matchesStatus;
  });
});

// Order form calculations
const calculatedItems = computed(() => {
  return form.value.items.map((entry) => {
    const quantity = Number(entry.quantity) || 0;
    const price = Number(entry.unit_price) || 0;
    const discount = Number(entry.discount_amount) || 0;
    const taxRate = Number(entry.tax_rate) || 0;

    const gross = quantity * price;
    const taxable = Math.max(0, gross - discount);
    const tax = (taxable * taxRate) / 100;

    return {
      ...entry,
      gross,
      taxable,
      tax,
      total: taxable + tax,
    };
  });
});

const orderTotals = computed(() => {
  return calculatedItems.value.reduce(
    (totals, item) => {
      totals.subtotal += item.gross;
      totals.discount += Number(item.discount_amount) || 0;
      totals.tax += item.tax;
      totals.total += item.total;
      return totals;
    },
    {
      subtotal: 0,
      discount: 0,
      tax: 0,
      total: 0,
    },
  );
});

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
  const classes = {
    DRAFT: "bg-secondary",
    SUBMITTED: "bg-warning text-dark",
    APPROVED: "bg-success",
    REJECTED: "bg-danger",
  };

  return classes[status] || "bg-secondary";
}

function formatStatus(status) {
  const translations = {
    DRAFT: "salesOrders.statuses.draft",
    SUBMITTED: "salesOrders.statuses.submitted",
    APPROVED: "salesOrders.statuses.approved",
    REJECTED: "salesOrders.statuses.rejected",
  };

  return translations[status] ? t(translations[status]) : status;
}

function getItemName(itemId) {
  return itemMap.value[itemId] || `Item #${itemId}`;
}

function resetForm() {
  form.value = {
    customer_id: "",
    notes: "",
    items: [
      {
        item_id: "",
        quantity: 1,
        unit_price: 0,
        discount_amount: 0,
        tax_rate: 5,
      },
    ],
  };

  error.value = "";
}

function openModal() {
  resetForm();
  showModal.value = true;
}

function addOrderItem() {
  form.value.items.push({
    item_id: "",
    quantity: 1,
    unit_price: 0,
    discount_amount: 0,
    tax_rate: 5,
  });
}

function removeOrderItem(index) {
  if (form.value.items.length === 1) return;
  form.value.items.splice(index, 1);
}

async function fetchOrders() {
  const response = await api.get("/sales-orders");
  salesOrders.value = response.data.sales_orders;
}

async function fetchCustomers() {
  const response = await api.get("/customers");
  customers.value = response.data.customers;
}

async function fetchItems() {
  const response = await api.get("/items");

  items.value = response.data.items.filter(
    (item) => item.is_active && item.category === "FINISHED_GOOD",
  );
}

async function loadData() {
  loading.value = true;
  error.value = "";

  try {
    await Promise.all([fetchOrders(), fetchCustomers(), fetchItems()]);
  } catch (err) {
    error.value = err.response?.data?.message || t("salesOrders.loadError");
  } finally {
    loading.value = false;
  }
}

function validateForm() {
  if (!form.value.customer_id) {
    return t("salesOrders.selectCustomerError");
  }

  if (!form.value.items.length) {
    return t("salesOrders.addProductError");
  }

  for (let i = 0; i < form.value.items.length; i++) {
    const item = form.value.items[i];

    if (!item.item_id) {
      return t("salesOrders.selectProductRowError", {
        row: i + 1,
      });
    }

    if (Number(item.quantity) <= 0) {
      return t("salesOrders.quantityError", {
        row: i + 1,
      });
    }

    if (Number(item.unit_price) < 0) {
      return t("salesOrders.priceError", {
        row: i + 1,
      });
    }

    if (Number(item.discount_amount) < 0) {
      return t("salesOrders.discountError", {
        row: i + 1,
      });
    }

    if (
      Number(item.discount_amount) >
      Number(item.quantity) * Number(item.unit_price)
    ) {
      return t("salesOrders.discountExceedsError", {
        row: i + 1,
      });
    }

    if (Number(item.tax_rate) < 0 || Number(item.tax_rate) > 100) {
      return t("salesOrders.gstError", {
        row: i + 1,
      });
    }
  }

  return "";
}

async function createOrder() {
  error.value = "";

  const validationError = validateForm();

  if (validationError) {
    error.value = validationError;
    return;
  }

  saving.value = true;

  try {
    const payload = {
      customer_id: Number(form.value.customer_id),
      notes: form.value.notes,
      items: form.value.items.map((item) => ({
        item_id: Number(item.item_id),
        quantity: Number(item.quantity),
        unit_price: Number(item.unit_price),
        discount_amount: Number(item.discount_amount),
        tax_rate: Number(item.tax_rate),
      })),
    };

    const response = await api.post("/sales-orders", payload);

    showModal.value = false;

    success.value = t("salesOrders.createSuccess", {
      number: response.data.sales_order.order_number,
    });

    await fetchOrders();
  } catch (err) {
    error.value = err.response?.data?.message || t("salesOrders.createError");
  } finally {
    saving.value = false;
  }
}

async function submitOrder(order) {
  if (
    !confirm(
      t("salesOrders.confirmSubmit", {
        number: order.order_number,
      }),
    )
  ) {
    return;
  }

  error.value = "";
  success.value = "";

  try {
    await api.post(`/sales-orders/${order.id}/submit`);

    success.value = t("salesOrders.submitSuccess");

    await fetchOrders();
  } catch (err) {
    error.value = err.response?.data?.message || t("salesOrders.submitError");
  }
}

async function reviewOrder(order, decision) {
  const action = decision === "APPROVED" ? "approve" : "reject";

  if (
    !confirm(
      t(
        decision === "APPROVED"
          ? "salesOrders.confirmApprove"
          : "salesOrders.confirmReject",
        { number: order.order_number },
      ),
    )
  ) {
    return;
  }

  error.value = "";
  success.value = "";

  try {
    await api.post(`/sales-orders/${order.id}/${action}`);

    success.value = t(
      decision === "APPROVED"
        ? "salesOrders.approveSuccess"
        : "salesOrders.rejectSuccess",
    );

    await fetchOrders();
  } catch (err) {
    error.value =
      err.response?.data?.message ||
      t(
        decision === "APPROVED"
          ? "salesOrders.approveError"
          : "salesOrders.rejectError",
      );
  }
}

onMounted(loadData);
</script>

<template>
  <div class="container-fluid py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold mb-1">
          {{ t("salesOrders.title") }}
        </h3>
        <p class="text-muted mb-0">
          {{ t("salesOrders.subtitle") }}
        </p>
      </div>

      <button class="btn btn-success" @click="openModal">
        + {{ t("salesOrders.newOrder") }}
      </button>
    </div>

    <!-- Notifications -->
    <div v-if="success" class="alert alert-success alert-dismissible">
      {{ success }}
      <button type="button" class="btn-close" @click="success = ''"></button>
    </div>

    <div v-if="error && !showModal" class="alert alert-danger">
      {{ error }}
    </div>

    <!-- Summary -->
    <div class="row g-3 mb-4">
      <div class="col-md-3">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <p class="text-muted small mb-1">
              {{ t("salesOrders.totalOrders") }}
            </p>
            <h4 class="fw-bold mb-0">
              {{ salesOrders.length }}
            </h4>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <p class="text-muted small mb-1">
              {{ t("salesOrders.draft") }}
            </p>
            <h4 class="fw-bold mb-0">
              {{ salesOrders.filter((o) => o.status === "DRAFT").length }}
            </h4>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <p class="text-muted small mb-1">
              {{ t("salesOrders.pendingApproval") }}
            </p>
            <h4 class="fw-bold mb-0">
              {{ salesOrders.filter((o) => o.status === "SUBMITTED").length }}
            </h4>
          </div>
        </div>
      </div>

      <div class="col-md-3">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <p class="text-muted small mb-1">
              {{ t("salesOrders.approved") }}
            </p>
            <h4 class="fw-bold mb-0">
              {{ salesOrders.filter((o) => o.status === "APPROVED").length }}
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
              :placeholder="t('salesOrders.searchPlaceholder')"
            />
          </div>

          <div class="col-md-4">
            <select v-model="statusFilter" class="form-select">
              <option value="ALL">
                {{ t("salesOrders.allStatuses") }}
              </option>
              <option value="DRAFT">
                {{ t("salesOrders.statuses.draft") }}
              </option>
              <option value="SUBMITTED">
                {{ t("salesOrders.statuses.submitted") }}
              </option>
              <option value="APPROVED">
                {{ t("salesOrders.statuses.approved") }}
              </option>
              <option value="REJECTED">
                {{ t("salesOrders.statuses.rejected") }}
              </option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Orders Table -->
    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-success"></div>
          <p class="text-muted mt-2">
            {{ t("salesOrders.loading") }}
          </p>
        </div>

        <div
          v-else-if="filteredOrders.length === 0"
          class="text-center text-muted py-5"
        >
          {{ t("salesOrders.noOrders") }}
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>{{ t("salesOrders.orderNumber") }}</th>
                <th>{{ t("salesOrders.date") }}</th>
                <th>{{ t("salesOrders.customer") }}</th>
                <th>{{ t("salesOrders.items") }}</th>
                <th>{{ t("salesOrders.totalAmount") }}</th>
                <th>{{ t("salesOrders.status") }}</th>
                <th>{{ t("salesOrders.actions") }}</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="order in filteredOrders" :key="order.id">
                <td class="fw-semibold">
                  {{ order.order_number }}
                </td>

                <td>{{ formatDate(order.order_date) }}</td>

                <td>
                  {{
                    customerMap[order.customer_id] ||
                    `Customer #${order.customer_id}`
                  }}
                </td>

                <td>{{ order.items.length }}</td>

                <td class="fw-semibold">
                  {{ formatCurrency(order.total_amount) }}
                </td>

                <td>
                  <span class="badge" :class="statusClass(order.status)">
                    {{ formatStatus(order.status) }}
                  </span>
                </td>

                <td>
                  <div class="d-flex gap-2">
                    <button
                      v-if="order.status === 'DRAFT'"
                      class="btn btn-sm btn-outline-primary"
                      @click="submitOrder(order)"
                    >
                      {{ t("salesOrders.submit") }}
                    </button>

                    <template v-if="order.status === 'SUBMITTED'">
                      <button
                        class="btn btn-sm btn-success"
                        @click="reviewOrder(order, 'APPROVED')"
                      >
                        {{ t("salesOrders.approve") }}
                      </button>

                      <button
                        class="btn btn-sm btn-outline-danger"
                        @click="reviewOrder(order, 'REJECTED')"
                      >
                        {{ t("salesOrders.reject") }}
                      </button>
                    </template>

                    <span
                      v-if="['APPROVED', 'REJECTED'].includes(order.status)"
                      class="text-muted small"
                    >
                      {{ t("salesOrders.reviewed") }}
                    </span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Create Sales Order Modal -->
    <div v-if="showModal" class="sales-overlay">
      <div class="sales-modal">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h5 class="fw-bold mb-1">
              {{ t("salesOrders.createOrder") }}
            </h5>
            <p class="text-muted small mb-0">
              {{ t("salesOrders.createSubtitle") }}
            </p>
          </div>

          <button
            class="btn-close"
            type="button"
            @click="showModal = false"
          ></button>
        </div>

        <form @submit.prevent="createOrder">
          <!-- Customer -->
          <div class="mb-4">
            <label class="form-label fw-semibold">
              {{ t("salesOrders.customer") }}
            </label>

            <select v-model="form.customer_id" class="form-select" required>
              <option value="" disabled>
                {{ t("salesOrders.selectCustomer") }}
              </option>

              <option
                v-for="customer in customers.filter((c) => c.is_active)"
                :key="customer.id"
                :value="customer.id"
              >
                {{ customer.business_name }}
              </option>
            </select>
          </div>

          <!-- Order Items -->
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h6 class="fw-bold mb-0">
              {{ t("salesOrders.orderItems") }}
            </h6>

            <button
              type="button"
              class="btn btn-sm btn-outline-success"
              @click="addOrderItem"
            >
              + {{ t("salesOrders.addProduct") }}
            </button>
          </div>

          <div
            v-for="(entry, index) in form.items"
            :key="index"
            class="order-item-box mb-3"
          >
            <div class="d-flex justify-content-between align-items-center mb-3">
              <span class="fw-semibold small">
                {{ t("salesOrders.productNumber", { number: index + 1 }) }}
              </span>

              <button
                v-if="form.items.length > 1"
                type="button"
                class="btn btn-sm btn-outline-danger"
                @click="removeOrderItem(index)"
              >
                {{ t("salesOrders.remove") }}
              </button>
            </div>

            <div class="mb-3">
              <label class="form-label small">
                {{ t("salesOrders.finishedProduct") }}
              </label>

              <select v-model="entry.item_id" class="form-select" required>
                <option value="" disabled>
                  {{ t("salesOrders.selectProduct") }}
                </option>

                <option v-for="item in items" :key="item.id" :value="item.id">
                  {{ item.name }} ({{ item.sku }})
                </option>
              </select>
            </div>

            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label small">
                  {{ t("salesOrders.quantity") }}
                </label>

                <input
                  v-model.number="entry.quantity"
                  type="number"
                  min="0.001"
                  step="0.001"
                  class="form-control"
                  required
                />
              </div>

              <div class="col-md-6">
                <label class="form-label small">
                  {{ t("salesOrders.unitPrice") }}
                </label>

                <input
                  v-model.number="entry.unit_price"
                  type="number"
                  min="0"
                  step="0.01"
                  class="form-control"
                  required
                />
              </div>

              <div class="col-md-6">
                <label class="form-label small">
                  {{ t("salesOrders.discount") }}
                </label>

                <input
                  v-model.number="entry.discount_amount"
                  type="number"
                  min="0"
                  step="0.01"
                  class="form-control"
                />
              </div>

              <div class="col-md-6">
                <label class="form-label small">
                  {{ t("salesOrders.gstRate") }}
                </label>

                <input
                  v-model.number="entry.tax_rate"
                  type="number"
                  min="0"
                  max="100"
                  step="0.01"
                  class="form-control"
                  required
                />
              </div>
            </div>

            <div class="text-end mt-3">
              <span class="text-muted small">
                {{ t("salesOrders.lineTotal") }}:
              </span>

              <strong>
                {{ formatCurrency(calculatedItems[index]?.total) }}
              </strong>
            </div>
          </div>

          <!-- Notes -->
          <div class="mb-4">
            <label class="form-label fw-semibold">
              {{ t("salesOrders.notes") }}
            </label>

            <textarea
              v-model="form.notes"
              class="form-control"
              rows="2"
              :placeholder="t('salesOrders.notesPlaceholder')"
            ></textarea>
          </div>

          <!-- Order Summary -->
          <div class="order-summary mb-4">
            <h6 class="fw-bold mb-3">
              {{ t("salesOrders.orderSummary") }}
            </h6>

            <div class="d-flex justify-content-between mb-2">
              <span>{{ t("salesOrders.subtotal") }}</span>
              <span>{{ formatCurrency(orderTotals.subtotal) }}</span>
            </div>

            <div class="d-flex justify-content-between mb-2">
              <span>{{ t("salesOrders.discount") }}</span>
              <span>{{ formatCurrency(orderTotals.discount) }}</span>
            </div>

            <div class="d-flex justify-content-between mb-2">
              <span>{{ t("salesOrders.gst") }}</span>
              <span>{{ formatCurrency(orderTotals.tax) }}</span>
            </div>

            <hr />

            <div class="d-flex justify-content-between">
              <strong>{{ t("salesOrders.totalAmount") }}</strong>

              <strong class="text-success fs-5">
                {{ formatCurrency(orderTotals.total) }}
              </strong>
            </div>

            <p class="text-muted small mt-2 mb-0">
              {{ t("salesOrders.backendCalculationNote") }}
            </p>
          </div>

          <!-- Error -->
          <div v-if="error" class="alert alert-danger">
            {{ error }}
          </div>

          <!-- Actions -->
          <div class="d-flex justify-content-end gap-2">
            <button
              type="button"
              class="btn btn-light"
              @click="showModal = false"
            >
              {{ t("salesOrders.cancel") }}
            </button>

            <button type="submit" class="btn btn-success" :disabled="saving">
              {{
                saving
                  ? t("salesOrders.creating")
                  : t("salesOrders.createDraft")
              }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sales-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  z-index: 1050;
}

.sales-modal {
  background: white;
  color: #212529;
  width: 100%;
  max-width: 750px;
  max-height: 92vh;
  overflow-y: auto;
  border-radius: 12px;
  padding: 24px;
}

.sales-modal .form-label {
  color: #343a40;
}

.order-item-box {
  border: 1px solid #dee2e6;
  border-radius: 10px;
  padding: 16px;
  background: #fafafa;
}

.order-summary {
  background: #f6f8f7;
  border-radius: 10px;
  padding: 18px;
}
</style>
