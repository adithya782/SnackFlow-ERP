<script setup>
import { ref, computed, onMounted } from "vue";
import api from "../services/api";

const inventory = ref([]);
const sales = ref(null);
const production = ref(null);
const receivables = ref(null);
const customers = ref([]);

const loading = ref(false);
const error = ref("");

const activeTab = ref("receivables");

const tabs = [
  { id: "receivables", label: "Receivables" },
  { id: "sales", label: "Sales" },
  { id: "inventory", label: "Inventory" },
  { id: "production", label: "Production" },
];

const formatCurrency = (value) => {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(Number(value || 0));
};

const formatDate = (value) => {
  if (!value) return "-";
  return new Date(value).toLocaleDateString("en-IN");
};

const loadReports = async () => {
  loading.value = true;
  error.value = "";

  try {
    const [
      inventoryResponse,
      salesResponse,
      productionResponse,
      receivablesResponse,
      customersResponse,
    ] = await Promise.all([
      api.get("/reports/inventory"),
      api.get("/reports/sales"),
      api.get("/reports/production"),
      api.get("/reports/receivables"),
      api.get("/customers"),
    ]);

    inventory.value = inventoryResponse.data;
    sales.value = salesResponse.data;
    production.value = productionResponse.data;
    receivables.value = receivablesResponse.data;
    customers.value = customersResponse.data.customers;
  } catch (err) {
    error.value =
      err.response?.data?.message ||
      "Unable to load reports. Check your login permissions.";
  } finally {
    loading.value = false;
  }
};

const customerMap = computed(() => {
  return Object.fromEntries(
    customers.value.map((customer) => [customer.id, customer.business_name]),
  );
});

const lowStockCount = computed(() => {
  return inventory.value.filter((item) => item.low_stock).length;
});

const completedRuns = computed(() => {
  return production.value?.completed_runs || 0;
});

const paymentPercentage = computed(() => {
  if (!receivables.value || Number(receivables.value.total_invoiced) === 0) {
    return 0;
  }

  return (
    (Number(receivables.value.total_paid) /
      Number(receivables.value.total_invoiced)) *
    100
  );
});

const paymentStatusLabel = (status) => {
  return (
    {
      PAID: "Paid",
      PARTIALLY_PAID: "Partially Paid",
      UNPAID: "Unpaid",
    }[status] || status
  );
};

onMounted(loadReports);
</script>

<template>
  <div class="reports-page">
    <div class="page-header">
      <div>
        <h2>Reports & Analytics</h2>
        <p>Monitor your business operations and financial performance.</p>
      </div>

      <button class="btn-refresh" @click="loadReports" :disabled="loading">
        {{ loading ? "Refreshing..." : "↻ Refresh Reports" }}
      </button>
    </div>

    <div v-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <div v-if="loading" class="loading-state">Loading business reports...</div>

    <template v-else-if="receivables && sales && production">
      <!-- SUMMARY CARDS -->

      <div class="summary-grid">
        <div class="summary-card">
          <span>Total Sales</span>
          <h3>{{ formatCurrency(sales.total_sales) }}</h3>
          <small>{{ sales.total_invoices }} issued invoices</small>
        </div>

        <div class="summary-card">
          <span>Total Outstanding</span>
          <h3 class="outstanding-number">
            {{ formatCurrency(receivables.total_outstanding) }}
          </h3>
          <small>Uncollected invoice balances</small>
        </div>

        <div class="summary-card">
          <span>Payments Received</span>
          <h3>{{ formatCurrency(receivables.total_paid) }}</h3>
          <small>Allocated against invoices</small>
        </div>

        <div class="summary-card">
          <span>Low Stock Items</span>
          <h3>{{ lowStockCount }}</h3>
          <small>Items at or below reorder level</small>
        </div>
      </div>

      <!-- REPORT NAVIGATION -->

      <div class="report-navigation">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- RECEIVABLES REPORT -->

      <div v-if="activeTab === 'receivables'" class="report-card">
        <div class="report-heading">
          <div>
            <h4>Receivables Report</h4>
            <p>Track outstanding customer invoice balances.</p>
          </div>
        </div>

        <div class="financial-summary">
          <div>
            <span>Total Invoiced</span>
            <strong>
              {{ formatCurrency(receivables.total_invoiced) }}
            </strong>
          </div>

          <div>
            <span>Total Paid</span>
            <strong class="paid-number">
              {{ formatCurrency(receivables.total_paid) }}
            </strong>
          </div>

          <div>
            <span>Total Outstanding</span>
            <strong class="outstanding-number">
              {{ formatCurrency(receivables.total_outstanding) }}
            </strong>
          </div>
        </div>

        <div class="progress-section">
          <div class="progress-label">
            <span>Collection Progress</span>
            <strong>{{ paymentPercentage.toFixed(1) }}%</strong>
          </div>

          <div class="progress-track">
            <div
              class="progress-fill"
              :style="{ width: `${Math.min(paymentPercentage, 100)}%` }"
            ></div>
          </div>
        </div>

        <div class="table-responsive">
          <table class="table align-middle">
            <thead>
              <tr>
                <th>Invoice Number</th>
                <th>Customer</th>
                <th>Invoice Total</th>
                <th>Paid</th>
                <th>Outstanding</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="invoice in receivables.invoices"
                :key="invoice.invoice_id"
              >
                <td class="fw-semibold">
                  {{ invoice.invoice_number }}
                </td>

                <td>{{ invoice.customer_name || "Unknown" }}</td>

                <td>{{ formatCurrency(invoice.invoice_total) }}</td>

                <td class="paid-number">
                  {{ formatCurrency(invoice.paid_amount) }}
                </td>

                <td class="outstanding-number">
                  {{ formatCurrency(invoice.outstanding_amount) }}
                </td>

                <td>
                  <span
                    class="status-badge"
                    :class="invoice.payment_status.toLowerCase()"
                  >
                    {{ paymentStatusLabel(invoice.payment_status) }}
                  </span>
                </td>
              </tr>

              <tr v-if="receivables.invoices.length === 0">
                <td colspan="6" class="empty-state">
                  No issued invoices found.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- SALES REPORT -->

      <div v-if="activeTab === 'sales'" class="report-card">
        <div class="report-heading">
          <div>
            <h4>Sales Report</h4>
            <p>Overview of issued invoices and sales revenue.</p>
          </div>
        </div>

        <div class="financial-summary">
          <div>
            <span>Total Sales</span>
            <strong>{{ formatCurrency(sales.total_sales) }}</strong>
          </div>

          <div>
            <span>Total Tax</span>
            <strong>{{ formatCurrency(sales.total_tax) }}</strong>
          </div>

          <div>
            <span>Invoices Issued</span>
            <strong>{{ sales.total_invoices }}</strong>
          </div>
        </div>

        <div class="table-responsive">
          <table class="table align-middle">
            <thead>
              <tr>
                <th>Invoice Number</th>
                <th>Customer</th>
                <th>Invoice Date</th>
                <th>Total Amount</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="invoice in sales.invoices" :key="invoice.invoice_id">
                <td class="fw-semibold">
                  {{ invoice.invoice_number }}
                </td>

                <td>
                  {{ customerMap[invoice.customer_id] || "Unknown" }}
                </td>

                <td>{{ formatDate(invoice.invoice_date) }}</td>

                <td>{{ formatCurrency(invoice.total_amount) }}</td>

                <td>
                  <span class="status-badge paid">
                    {{ invoice.status }}
                  </span>
                </td>
              </tr>

              <tr v-if="sales.invoices.length === 0">
                <td colspan="5" class="empty-state">No sales records found.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- INVENTORY REPORT -->

      <div v-if="activeTab === 'inventory'" class="report-card">
        <div class="report-heading">
          <div>
            <h4>Inventory Report</h4>
            <p>Current stock levels and reorder requirements.</p>
          </div>
        </div>

        <div class="financial-summary">
          <div>
            <span>Total Active Items</span>
            <strong>{{ inventory.length }}</strong>
          </div>

          <div>
            <span>Low Stock Items</span>
            <strong class="outstanding-number">
              {{ lowStockCount }}
            </strong>
          </div>

          <div>
            <span>Healthy Stock Items</span>
            <strong class="paid-number">
              {{ inventory.length - lowStockCount }}
            </strong>
          </div>
        </div>

        <div class="table-responsive">
          <table class="table align-middle">
            <thead>
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
                <td>{{ item.category.replace("_", " ") }}</td>
                <td>{{ item.current_stock }} {{ item.unit }}</td>
                <td>{{ item.reorder_level }} {{ item.unit }}</td>

                <td>
                  <span
                    class="status-badge"
                    :class="item.low_stock ? 'unpaid' : 'paid'"
                  >
                    {{ item.low_stock ? "Low Stock" : "Healthy" }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- PRODUCTION REPORT -->

      <div v-if="activeTab === 'production'" class="report-card">
        <div class="report-heading">
          <div>
            <h4>Production Report</h4>
            <p>Production runs, output and material costs.</p>
          </div>
        </div>

        <div class="financial-summary">
          <div>
            <span>Total Production Runs</span>
            <strong>{{ production.total_runs }}</strong>
          </div>

          <div>
            <span>Completed Runs</span>
            <strong class="paid-number">{{ completedRuns }}</strong>
          </div>

          <div>
            <span>Other Runs</span>
            <strong>
              {{ production.total_runs - completedRuns }}
            </strong>
          </div>
        </div>

        <div class="table-responsive">
          <table class="table align-middle">
            <thead>
              <tr>
                <th>Run Number</th>
                <th>Date</th>
                <th>Planned Output</th>
                <th>Actual Output</th>
                <th>Material Cost</th>
                <th>Cost / Unit</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="run in production.production_runs"
                :key="run.production_run_id"
              >
                <td class="fw-semibold">{{ run.run_number }}</td>
                <td>{{ formatDate(run.production_date) }}</td>
                <td>{{ run.planned_output }}</td>
                <td>{{ run.actual_output ?? "-" }}</td>
                <td>{{ formatCurrency(run.material_cost) }}</td>
                <td>{{ formatCurrency(run.cost_per_unit) }}</td>

                <td>
                  <span
                    class="status-badge"
                    :class="run.status === 'COMPLETED' ? 'paid' : 'unpaid'"
                  >
                    {{ run.status }}
                  </span>
                </td>
              </tr>

              <tr v-if="production.production_runs.length === 0">
                <td colspan="7" class="empty-state">
                  No production runs found.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.reports-page {
  padding: 8px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
  margin-bottom: 25px;
}

.page-header h2 {
  color: #183b2b;
  font-size: 25px;
  font-weight: 700;
  margin-bottom: 5px;
}

.page-header p,
.report-heading p {
  color: #78847e;
  font-size: 14px;
  margin: 0;
}

.btn-refresh {
  border: 1px solid #d8e1db;
  background: white;
  color: #176b45;
  border-radius: 7px;
  padding: 9px 14px;
  font-weight: 600;
}

.btn-refresh:disabled {
  opacity: 0.6;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.summary-card,
.report-card {
  background: white;
  border: 1px solid #e8eeea;
  border-radius: 10px;
  padding: 20px;
}

.summary-card span,
.financial-summary span {
  color: #78847e;
  font-size: 13px;
  display: block;
  margin-bottom: 9px;
}

.summary-card h3 {
  color: #183b2b;
  font-size: 23px;
  font-weight: 700;
  margin: 0 0 7px;
}

.summary-card small {
  color: #89958d;
  font-size: 12px;
}

.outstanding-number {
  color: #b45b24 !important;
}

.paid-number {
  color: #187345 !important;
}

.report-navigation {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 18px;
}

.report-navigation button {
  padding: 10px 18px;
  border-radius: 7px;
  border: 1px solid #dce5df;
  background: white;
  color: #53645a;
  font-weight: 600;
  font-size: 13px;
}

.report-navigation button.active {
  background: #176b45;
  border-color: #176b45;
  color: white;
}

.report-card {
  margin-bottom: 25px;
}

.report-heading {
  margin-bottom: 22px;
}

.report-heading h4 {
  color: #183b2b;
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 5px;
}

.financial-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  padding: 18px;
  background: #f5f8f6;
  border-radius: 8px;
  margin-bottom: 22px;
}

.financial-summary strong {
  color: #244b35;
  font-size: 19px;
}

.progress-section {
  margin-bottom: 24px;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 9px;
  font-size: 13px;
  color: #53645a;
}

.progress-track {
  height: 10px;
  background: #e5ece7;
  border-radius: 20px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #26965d;
  border-radius: 20px;
  transition: width 0.3s ease;
}

.table {
  min-width: 850px;
  margin-bottom: 0;
}

.table thead th {
  background: #f5f8f6;
  color: #627067;
  font-size: 12px;
  text-transform: uppercase;
  padding: 13px;
  white-space: nowrap;
}

.table tbody td {
  padding: 14px 13px;
  color: #34443a;
  font-size: 13px;
}

.status-badge {
  display: inline-block;
  border-radius: 20px;
  padding: 5px 10px;
  font-size: 11px;
  font-weight: 700;
  white-space: nowrap;
}

.status-badge.paid {
  background: #e3f5eb;
  color: #187345;
}

.status-badge.partially_paid {
  background: #fff1d9;
  color: #a76516;
}

.status-badge.unpaid {
  background: #fce9e7;
  color: #b43d34;
}

.empty-state,
.loading-state {
  text-align: center;
  padding: 35px;
  color: #849087;
}

@media (max-width: 1100px) {
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .financial-summary {
    grid-template-columns: 1fr;
  }
}
</style>
