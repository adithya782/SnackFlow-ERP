<script setup>
import { ref, onMounted, computed } from "vue";
import { useI18n } from "vue-i18n";
import api from "../services/api";

const { t } = useI18n();

const purchases = ref([]);
const suppliers = ref([]);
const items = ref([]);
const loading = ref(true);
const error = ref("");
const saving = ref(false);
const showModal = ref(false);
const searchQuery = ref("");

const form = ref({
  supplier_id: "",
  notes: "",
  items: [{ item_id: "", quantity: "", unit_price: "", gst_rate: 0 }],
});

const filteredPurchases = computed(() => {
  return purchases.value.filter(
    (purchase) =>
      String(purchase.purchase_number || purchase.id)
        .toLowerCase()
        .includes(searchQuery.value.toLowerCase()) ||
      String(purchase.supplier_name || "")
        .toLowerCase()
        .includes(searchQuery.value.toLowerCase()),
  );
});
const supplierMap = computed(() => {
  return Object.fromEntries(
    suppliers.value.map((supplier) => [supplier.id, supplier.business_name]),
  );
});
async function fetchData() {
  loading.value = true;
  error.value = "";

  try {
    const [purchaseResponse, supplierResponse, itemResponse] =
      await Promise.all([
        api.get("/purchases"),
        api.get("/suppliers"),
        api.get("/items"),
      ]);

    purchases.value = purchaseResponse.data.purchases;
    suppliers.value = supplierResponse.data.suppliers;
    items.value = itemResponse.data.items;
  } catch (err) {
    error.value = err.response?.data?.message || t("purchases.loadError");
  } finally {
    loading.value = false;
  }
}

function openModal() {
  error.value = "";

  form.value = {
    supplier_id: "",
    notes: "",
    items: [{ item_id: "", quantity: "", unit_price: "", gst_rate: 0 }],
  };

  showModal.value = true;
}

function addItem() {
  form.value.items.push({
    item_id: "",
    quantity: "",
    unit_price: "",
    gst_rate: 0,
  });
}

function removeItem(index) {
  if (form.value.items.length > 1) {
    form.value.items.splice(index, 1);
  }
}

async function createPurchase() {
  saving.value = true;
  error.value = "";

  try {
    const payload = {
      supplier_id: Number(form.value.supplier_id),
      notes: form.value.notes,
      items: form.value.items.map((item) => ({
        item_id: Number(item.item_id),
        quantity: Number(item.quantity),
        unit_price: Number(item.unit_price),
        tax_rate: Number(item.gst_rate),
      })),
    };

    await api.post("/purchases", payload);

    showModal.value = false;
    await fetchData();
  } catch (err) {
    error.value = err.response?.data?.message || t("purchases.createError");
  } finally {
    saving.value = false;
  }
}

async function receivePurchase(purchase) {
  if (!confirm(t("purchases.confirmReceive"))) {
    return;
  }

  error.value = "";

  try {
    await api.post(`/purchases/${purchase.id}/receive`);
    await fetchData();
    alert(t("purchases.receiveSuccess"));
  } catch (err) {
    error.value = err.response?.data?.message || t("purchases.receiveError");
  }
}

function formatCurrency(value) {
  return Number(value || 0).toLocaleString("en-IN", {
    style: "currency",
    currency: "INR",
  });
}

function formatDate(value) {
  if (!value) return "-";
  return new Date(value).toLocaleDateString("en-IN");
}

function formatStatus(status) {
  const statuses = {
    DRAFT: "purchases.statuses.draft",
    RECEIVED: "purchases.statuses.received",
  };

  return statuses[status] ? t(statuses[status]) : status;
}

onMounted(fetchData);
</script>

<template>
  <div class="container-fluid py-3">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold mb-1">{{ t("purchases.title") }}</h3>
        <p class="text-muted mb-0">
          {{ t("purchases.subtitle") }}
        </p>
      </div>

      <button class="btn btn-success" @click="openModal">
        + {{ t("purchases.newPurchase") }}
      </button>
    </div>

    <div v-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <div class="card border-0 shadow-sm mb-3">
      <div class="card-body">
        <input
          v-model="searchQuery"
          class="form-control"
          :placeholder="t('purchases.searchPlaceholder')"
        />
      </div>
    </div>

    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          {{ t("purchases.loading") }}
        </div>

        <div
          v-else-if="filteredPurchases.length === 0"
          class="text-center py-5 text-muted"
        >
          {{ t("purchases.noPurchases") }}
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th>{{ t("purchases.purchaseNumber") }}</th>
                <th>{{ t("purchases.supplier") }}</th>
                <th>{{ t("purchases.date") }}</th>
                <th>{{ t("purchases.total") }}</th>
                <th>{{ t("purchases.status") }}</th>
                <th>{{ t("purchases.action") }}</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="purchase in filteredPurchases" :key="purchase.id">
                <td class="fw-semibold">
                  {{ purchase.purchase_number || `PUR-${purchase.id}` }}
                </td>

                <td>
                  {{
                    purchase.supplier_name ||
                    supplierMap[purchase.supplier_id] ||
                    "-"
                  }}
                </td>

                <td>
                  {{
                    formatDate(purchase.purchase_date || purchase.created_at)
                  }}
                </td>

                <td>{{ formatCurrency(purchase.total_amount) }}</td>

                <td>
                  <span
                    class="badge"
                    :class="
                      purchase.status === 'RECEIVED'
                        ? 'bg-success'
                        : 'bg-warning text-dark'
                    "
                  >
                    {{ formatStatus(purchase.status) }}
                  </span>
                </td>

                <td>
                  <button
                    v-if="purchase.status === 'DRAFT'"
                    class="btn btn-sm btn-outline-success"
                    @click="receivePurchase(purchase)"
                  >
                    {{ t("purchases.receive") }}
                  </button>

                  <span v-else class="text-success small">
                    ✓ {{ t("purchases.received") }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- New Purchase Modal -->
    <div v-if="showModal" class="purchase-overlay">
      <div class="purchase-modal">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h5 class="fw-bold mb-0">
            {{ t("purchases.createNewPurchase") }}
          </h5>

          <button class="btn-close" @click="showModal = false"></button>
        </div>

        <form @submit.prevent="createPurchase">
          <div class="mb-3">
            <label class="form-label fw-semibold">
              {{ t("purchases.supplier") }}
            </label>

            <select v-model="form.supplier_id" class="form-select" required>
              <option value="" disabled>
                {{ t("purchases.selectSupplier") }}
              </option>

              <option
                v-for="supplier in suppliers.filter((s) => s.is_active)"
                :key="supplier.id"
                :value="supplier.id"
              >
                {{ supplier.business_name }}
              </option>
            </select>
          </div>

          <hr />

          <div class="d-flex justify-content-between align-items-center mb-3">
            <h6 class="fw-bold mb-0">
              {{ t("purchases.purchaseItems") }}
            </h6>

            <button
              type="button"
              class="btn btn-sm btn-outline-success"
              @click="addItem"
            >
              + {{ t("purchases.addItem") }}
            </button>
          </div>

          <div
            v-for="(item, index) in form.items"
            :key="index"
            class="purchase-item mb-3"
          >
            <div class="d-flex justify-content-between mb-2">
              <strong>
                {{ t("purchases.itemNumber", { number: index + 1 }) }}
              </strong>

              <button
                v-if="form.items.length > 1"
                type="button"
                class="btn btn-sm btn-outline-danger"
                @click="removeItem(index)"
              >
                {{ t("purchases.remove") }}
              </button>
            </div>

            <div class="mb-2">
              <label class="form-label">
                {{ t("purchases.materialItem") }}
              </label>

              <select v-model="item.item_id" class="form-select" required>
                <option value="" disabled>
                  {{ t("purchases.selectItem") }}
                </option>

                <option
                  v-for="product in items.filter(
                    (p) => p.is_active && p.category !== 'FINISHED_GOOD',
                  )"
                  :key="product.id"
                  :value="product.id"
                >
                  {{ product.name }} ({{ product.unit }})
                </option>
              </select>
            </div>

            <div class="row g-2">
              <div class="col-4">
                <label class="form-label">
                  {{ t("purchases.quantity") }}
                </label>

                <input
                  v-model="item.quantity"
                  type="number"
                  min="0.001"
                  step="0.001"
                  class="form-control"
                  required
                />
              </div>

              <div class="col-4">
                <label class="form-label">
                  {{ t("purchases.rate") }}
                </label>

                <input
                  v-model="item.unit_price"
                  type="number"
                  min="0.01"
                  step="0.01"
                  class="form-control"
                  required
                />
              </div>

              <div class="col-4">
                <label class="form-label">
                  {{ t("purchases.gstRate") }}
                </label>

                <input
                  v-model="item.gst_rate"
                  type="number"
                  min="0"
                  step="0.01"
                  class="form-control"
                  required
                />
              </div>
            </div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold">
              {{ t("purchases.notes") }}
            </label>

            <textarea
              v-model="form.notes"
              class="form-control"
              rows="2"
              :placeholder="t('purchases.optional')"
            ></textarea>
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
              {{ t("purchases.cancel") }}
            </button>

            <button type="submit" class="btn btn-success" :disabled="saving">
              {{ saving ? t("purchases.saving") : t("purchases.savePurchase") }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.purchase-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  z-index: 1050;
}

.purchase-modal {
  background: white;
  color: #212529;
  width: 100%;
  max-width: 620px;
  max-height: 90vh;
  overflow-y: auto;
  border-radius: 12px;
  padding: 24px;
}

.purchase-item {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  padding: 15px;
  border-radius: 9px;
}

.purchase-modal .form-label {
  color: #343a40;
  font-size: 14px;
}
</style>
