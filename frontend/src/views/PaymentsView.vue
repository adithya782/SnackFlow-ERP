<script setup>
import { ref, computed, onMounted } from "vue";
import api from "../services/api";

const payments = ref([]);
const invoices = ref([]);
const customers = ref([]);

const loading = ref(false);
const saving = ref(false);
const error = ref("");
const success = ref("");

const showPaymentForm = ref(false);

const paymentForm = ref({
  customer_id: "",
  amount: "",
  payment_method: "UPI",
  reference_number: "",
  notes: "",
});

const allocationForm = ref({
  payment_id: "",
  invoice_id: "",
  allocated_amount: "",
});

const outstanding = ref(null);
const checkingOutstanding = ref(false);

const paymentMethods = ["CASH", "UPI", "BANK_TRANSFER", "CHEQUE", "OTHER"];

const customerMap = computed(() => {
  return Object.fromEntries(
    customers.value.map((customer) => [customer.id, customer.business_name]),
  );
});

const invoiceMap = computed(() => {
  return Object.fromEntries(
    invoices.value.map((invoice) => [invoice.id, invoice.invoice_number]),
  );
});

const selectedPayment = computed(() => {
  return payments.value.find(
    (payment) => payment.id === Number(allocationForm.value.payment_id),
  );
});

const eligibleInvoices = computed(() => {
  if (!selectedPayment.value) return [];

  return invoices.value.filter(
    (invoice) =>
      invoice.customer_id === selectedPayment.value.customer_id &&
      invoice.status === "ISSUED",
  );
});

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

const clearMessages = () => {
  error.value = "";
  success.value = "";
};

const loadData = async () => {
  loading.value = true;
  error.value = "";

  try {
    const [paymentResponse, invoiceResponse, customerResponse] =
      await Promise.all([
        api.get("/payments"),
        api.get("/invoices"),
        api.get("/customers"),
      ]);

    payments.value = paymentResponse.data;
    invoices.value = invoiceResponse.data.invoices;
    customers.value = customerResponse.data.customers;
  } catch (err) {
    error.value =
      err.response?.data?.message || "Unable to load payment information.";
  } finally {
    loading.value = false;
  }
};

const resetPaymentForm = () => {
  paymentForm.value = {
    customer_id: "",
    amount: "",
    payment_method: "UPI",
    reference_number: "",
    notes: "",
  };
};

const recordPayment = async () => {
  clearMessages();

  if (
    !paymentForm.value.customer_id ||
    !paymentForm.value.amount ||
    Number(paymentForm.value.amount) <= 0
  ) {
    error.value = "Please select a customer and enter a valid amount.";
    return;
  }

  saving.value = true;

  try {
    await api.post("/payments", {
      customer_id: Number(paymentForm.value.customer_id),
      amount: Number(paymentForm.value.amount),
      payment_method: paymentForm.value.payment_method,
      reference_number: paymentForm.value.reference_number,
      notes: paymentForm.value.notes,
    });

    success.value = "Payment recorded successfully.";

    showPaymentForm.value = false;
    resetPaymentForm();

    await loadData();
  } catch (err) {
    error.value = err.response?.data?.message || "Unable to record payment.";
  } finally {
    saving.value = false;
  }
};

const resetAllocation = () => {
  allocationForm.value = {
    payment_id: "",
    invoice_id: "",
    allocated_amount: "",
  };

  outstanding.value = null;
};

const onPaymentSelected = () => {
  allocationForm.value.invoice_id = "";
  allocationForm.value.allocated_amount = "";
  outstanding.value = null;
};

const checkOutstanding = async () => {
  clearMessages();
  outstanding.value = null;

  if (!allocationForm.value.invoice_id) return;

  checkingOutstanding.value = true;

  try {
    const response = await api.get(
      `/payments/invoice/${allocationForm.value.invoice_id}/outstanding`,
    );

    outstanding.value = response.data;
  } catch (err) {
    error.value =
      err.response?.data?.message ||
      "Unable to check invoice outstanding amount.";
  } finally {
    checkingOutstanding.value = false;
  }
};

const allocatePayment = async () => {
  clearMessages();

  if (
    !allocationForm.value.payment_id ||
    !allocationForm.value.invoice_id ||
    !allocationForm.value.allocated_amount ||
    Number(allocationForm.value.allocated_amount) <= 0
  ) {
    error.value = "Please complete all allocation fields.";
    return;
  }

  saving.value = true;

  try {
    await api.post(`/payments/${allocationForm.value.payment_id}/allocate`, {
      invoice_id: Number(allocationForm.value.invoice_id),
      allocated_amount: Number(allocationForm.value.allocated_amount),
    });

    success.value = "Payment allocated successfully.";

    resetAllocation();
    await loadData();
  } catch (err) {
    error.value = err.response?.data?.message || "Unable to allocate payment.";
  } finally {
    saving.value = false;
  }
};

const totalReceived = computed(() => {
  return payments.value.reduce(
    (total, payment) => total + Number(payment.amount || 0),
    0,
  );
});

const totalInvoiceValue = computed(() => {
  return invoices.value
    .filter((invoice) => invoice.status === "ISSUED")
    .reduce((total, invoice) => total + Number(invoice.total_amount || 0), 0);
});

onMounted(loadData);
</script>

<template>
  <div class="payments-page">
    <div class="page-header">
      <div>
        <h2>Payments & Receivables</h2>
        <p>Manage customer payments and invoice allocations.</p>
      </div>

      <button
        class="btn-primary-custom"
        @click="
          showPaymentForm = true;
          clearMessages();
        "
      >
        + Record Payment
      </button>
    </div>

    <div v-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <div v-if="success" class="alert alert-success">
      {{ success }}
    </div>

    <div class="summary-grid">
      <div class="summary-card">
        <span>Total Payments Received</span>
        <h3>{{ formatCurrency(totalReceived) }}</h3>
      </div>

      <div class="summary-card">
        <span>Issued Invoice Value</span>
        <h3>{{ formatCurrency(totalInvoiceValue) }}</h3>
      </div>

      <div class="summary-card">
        <span>Payment Records</span>
        <h3>{{ payments.length }}</h3>
      </div>

      <div class="summary-card">
        <span>Issued Invoices</span>
        <h3>
          {{ invoices.filter((i) => i.status === "ISSUED").length }}
        </h3>
      </div>
    </div>

    <!-- PAYMENT RECORDS -->

    <div class="content-card">
      <div class="section-header">
        <div>
          <h4>Payment Records</h4>
          <p>Money received from customers</p>
        </div>

        <button class="btn-refresh" @click="loadData">Refresh</button>
      </div>

      <div v-if="loading" class="empty-state">Loading payments...</div>

      <div v-else-if="payments.length === 0" class="empty-state">
        No payment records found.
      </div>

      <div v-else class="table-responsive">
        <table class="table align-middle">
          <thead>
            <tr>
              <th>Payment Number</th>
              <th>Customer</th>
              <th>Date</th>
              <th>Amount</th>
              <th>Method</th>
              <th>Reference</th>
              <th>Status</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="payment in payments" :key="payment.id">
              <td class="fw-semibold">
                {{ payment.payment_number }}
              </td>

              <td>
                {{ customerMap[payment.customer_id] || "Unknown" }}
              </td>

              <td>{{ formatDate(payment.payment_date) }}</td>

              <td class="fw-semibold">
                {{ formatCurrency(payment.amount) }}
              </td>

              <td>
                {{ payment.payment_method.replace("_", " ") }}
              </td>

              <td>{{ payment.reference_number || "-" }}</td>

              <td>
                <span class="status-badge">
                  {{ payment.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- PAYMENT ALLOCATION -->

    <div class="content-card allocation-card">
      <div class="section-header">
        <div>
          <h4>Allocate Payment to Invoice</h4>
          <p>Apply a received payment against a customer's invoice.</p>
        </div>
      </div>

      <div class="allocation-form">
        <div class="form-group">
          <label>Select Payment</label>

          <select
            v-model="allocationForm.payment_id"
            class="form-select"
            @change="onPaymentSelected"
          >
            <option value="">Choose a payment</option>

            <option
              v-for="payment in payments.filter((p) => p.status === 'RECEIVED')"
              :key="payment.id"
              :value="payment.id"
            >
              {{ payment.payment_number }} —
              {{ customerMap[payment.customer_id] || "Unknown" }} —
              {{ formatCurrency(payment.amount) }}
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>Select Invoice</label>

          <select
            v-model="allocationForm.invoice_id"
            class="form-select"
            :disabled="!selectedPayment"
            @change="checkOutstanding"
          >
            <option value="">Choose an invoice</option>

            <option
              v-for="invoice in eligibleInvoices"
              :key="invoice.id"
              :value="invoice.id"
            >
              {{ invoice.invoice_number }} —
              {{ formatCurrency(invoice.total_amount) }}
            </option>
          </select>

          <small v-if="selectedPayment">
            Only issued invoices belonging to the selected customer are shown.
          </small>
        </div>

        <div v-if="outstanding" class="outstanding-panel">
          <div>
            <span>Invoice Total</span>
            <strong>{{ formatCurrency(outstanding.invoice_total) }}</strong>
          </div>

          <div>
            <span>Already Paid</span>
            <strong>{{ formatCurrency(outstanding.paid_amount) }}</strong>
          </div>

          <div>
            <span>Outstanding</span>
            <strong class="outstanding-value">
              {{ formatCurrency(outstanding.outstanding_amount) }}
            </strong>
          </div>
        </div>

        <div v-if="checkingOutstanding" class="text-muted">
          Checking invoice balance...
        </div>

        <div class="form-group">
          <label>Allocation Amount (₹)</label>

          <input
            v-model="allocationForm.allocated_amount"
            type="number"
            min="0.01"
            step="0.01"
            class="form-control"
            placeholder="Enter amount to allocate"
            :disabled="!outstanding"
          />
        </div>

        <div class="allocation-note">
          The backend validates the available payment amount and invoice
          outstanding balance before saving an allocation.
        </div>

        <button
          class="btn-primary-custom"
          @click="allocatePayment"
          :disabled="saving || !outstanding"
        >
          {{ saving ? "Processing..." : "Allocate Payment" }}
        </button>
      </div>
    </div>

    <!-- RECORD PAYMENT MODAL -->

    <div
      v-if="showPaymentForm"
      class="modal-overlay"
      @click.self="showPaymentForm = false"
    >
      <div class="payment-modal">
        <div class="modal-header-custom">
          <div>
            <h4>Record Customer Payment</h4>
            <p>Enter the payment received from a customer.</p>
          </div>

          <button class="close-btn" @click="showPaymentForm = false">
            &times;
          </button>
        </div>

        <form @submit.prevent="recordPayment">
          <div class="form-group">
            <label>Customer *</label>

            <select
              v-model="paymentForm.customer_id"
              class="form-select"
              required
            >
              <option value="">Select customer</option>

              <option
                v-for="customer in customers.filter((c) => c.is_active)"
                :key="customer.id"
                :value="customer.id"
              >
                {{ customer.business_name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Amount (₹) *</label>

            <input
              v-model="paymentForm.amount"
              type="number"
              min="0.01"
              step="0.01"
              class="form-control"
              placeholder="Enter amount received"
              required
            />
          </div>

          <div class="form-group">
            <label>Payment Method *</label>

            <select
              v-model="paymentForm.payment_method"
              class="form-select"
              required
            >
              <option
                v-for="method in paymentMethods"
                :key="method"
                :value="method"
              >
                {{ method.replace("_", " ") }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Reference Number</label>

            <input
              v-model="paymentForm.reference_number"
              type="text"
              class="form-control"
              placeholder="UPI transaction ID / cheque number"
            />
          </div>

          <div class="form-group">
            <label>Notes</label>

            <textarea
              v-model="paymentForm.notes"
              class="form-control"
              rows="3"
              placeholder="Optional payment notes"
            ></textarea>
          </div>

          <div class="modal-actions">
            <button
              type="button"
              class="btn-cancel"
              @click="showPaymentForm = false"
            >
              Cancel
            </button>

            <button type="submit" class="btn-primary-custom" :disabled="saving">
              {{ saving ? "Saving..." : "Save Payment" }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.payments-page {
  padding: 8px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  gap: 15px;
}

.page-header h2 {
  font-size: 25px;
  font-weight: 700;
  color: #183b2b;
  margin-bottom: 5px;
}

.page-header p,
.section-header p,
.modal-header-custom p {
  color: #78847e;
  margin: 0;
  font-size: 14px;
}

.btn-primary-custom {
  background: #176b45;
  color: white;
  border: none;
  border-radius: 7px;
  padding: 10px 17px;
  font-weight: 600;
}

.btn-primary-custom:hover {
  background: #105538;
}

.btn-primary-custom:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.summary-card,
.content-card {
  background: white;
  border: 1px solid #e8eeea;
  border-radius: 10px;
  padding: 20px;
}

.summary-card span {
  display: block;
  color: #758078;
  font-size: 13px;
  margin-bottom: 10px;
}

.summary-card h3 {
  color: #183b2b;
  font-size: 23px;
  font-weight: 700;
  margin: 0;
}

.content-card {
  margin-bottom: 22px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 12px;
}

.section-header h4,
.modal-header-custom h4 {
  font-size: 17px;
  font-weight: 700;
  color: #183b2b;
  margin-bottom: 5px;
}

.btn-refresh,
.btn-cancel {
  background: white;
  border: 1px solid #d8e1db;
  color: #355344;
  padding: 8px 14px;
  border-radius: 6px;
  font-weight: 600;
}

.table {
  min-width: 850px;
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
  font-size: 13px;
  color: #34443a;
}

.status-badge {
  background: #e3f5eb;
  color: #187345;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 700;
}

.empty-state {
  text-align: center;
  padding: 35px;
  color: #849087;
}

.allocation-form {
  max-width: 650px;
}

.form-group {
  margin-bottom: 17px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #34443a;
  margin-bottom: 7px;
}

.form-control,
.form-select {
  padding: 10px 12px;
  font-size: 14px;
  border-color: #dce5df;
}

.form-control:focus,
.form-select:focus {
  border-color: #4a9b72;
  box-shadow: 0 0 0 3px rgba(40, 130, 80, 0.1);
}

.form-group small {
  display: block;
  color: #849087;
  margin-top: 6px;
}

.outstanding-panel {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  background: #f4f8f5;
  padding: 17px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.outstanding-panel div {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.outstanding-panel span {
  font-size: 12px;
  color: #78847e;
}

.outstanding-panel strong {
  font-size: 15px;
  color: #244b35;
}

.outstanding-panel .outstanding-value {
  color: #b45b24;
}

.allocation-note {
  background: #f5f7f6;
  border-left: 3px solid #6b9d7e;
  padding: 12px;
  margin-bottom: 18px;
  color: #647269;
  font-size: 12px;
  line-height: 1.5;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 30, 21, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 1050;
}

.payment-modal {
  background: white;
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  overflow-y: auto;
  border-radius: 12px;
  padding: 25px;
}

.modal-header-custom {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 22px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 27px;
  color: #78847e;
  cursor: pointer;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 22px;
}

@media (max-width: 1000px) {
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

  .outstanding-panel {
    grid-template-columns: 1fr;
  }

  .payment-modal {
    padding: 18px;
  }
}
</style>
