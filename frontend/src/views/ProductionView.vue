<script setup>
import { ref, onMounted, computed } from "vue";
import api from "../services/api";

const productionRuns = ref([]);
const boms = ref([]);
const loading = ref(true);
const saving = ref(false);
const showModal = ref(false);
const error = ref("");

const form = ref({
  bom_id: "",
  planned_output: "",
});

const selectedBom = computed(() =>
  boms.value.find((bom) => bom.id === Number(form.value.bom_id)),
);

const plannedMaterials = computed(() => {
  if (!selectedBom.value || !Number(form.value.planned_output)) {
    return [];
  }

  const scale =
    Number(form.value.planned_output) /
    Number(selectedBom.value.output_quantity);

  return selectedBom.value.materials.map((material) => ({
    ...material,
    required_quantity: (Number(material.quantity) * scale).toFixed(3),
  }));
});

async function fetchProduction() {
  loading.value = true;
  error.value = "";

  try {
    const response = await api.get("/production");
    productionRuns.value = response.data.production_runs;
  } catch (err) {
    error.value =
      err.response?.data?.message || "Failed to load production records.";
  } finally {
    loading.value = false;
  }
}

async function fetchBoms() {
  try {
    const response = await api.get("/boms");
    boms.value = response.data.boms;
  } catch (err) {
    error.value =
      err.response?.data?.message || "Failed to load Bills of Materials.";
  }
}

function openModal() {
  form.value = {
    bom_id: "",
    planned_output: "",
  };

  error.value = "";
  showModal.value = true;
}

async function createProductionRun() {
  saving.value = true;
  error.value = "";

  try {
    await api.post("/production/runs", {
      bom_id: Number(form.value.bom_id),
      planned_output: Number(form.value.planned_output),
    });

    showModal.value = false;
    await fetchProduction();
  } catch (err) {
    error.value =
      err.response?.data?.message || "Failed to create production run.";
  } finally {
    saving.value = false;
  }
}

function formatDate(date) {
  if (!date) return "-";

  return new Date(date).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function statusClass(status) {
  const classes = {
    PLANNED: "bg-secondary",
    IN_PROGRESS: "bg-primary",
    COMPLETED: "bg-success",
    CANCELLED: "bg-danger",
  };

  return classes[status] || "bg-secondary";
}

onMounted(async () => {
  await Promise.all([fetchProduction(), fetchBoms()]);
});
</script>

<template>
  <div class="container-fluid py-4">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold mb-1">Production</h3>
        <p class="text-muted mb-0">
          Manage manufacturing runs and finished goods.
        </p>
      </div>

      <button class="btn btn-success" @click="openModal">
        + New Production Run
      </button>
    </div>

    <!-- Error Message -->
    <div v-if="error && !showModal" class="alert alert-danger">
      {{ error }}
    </div>

    <!-- Production Table -->
    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-success"></div>
          <p class="text-muted mt-2 mb-0">Loading production records...</p>
        </div>

        <div
          v-else-if="productionRuns.length === 0"
          class="text-center text-muted py-5"
        >
          No production runs found.
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>Run Number</th>
                <th>Date</th>
                <th>Planned Output</th>
                <th>Actual Output</th>
                <th>Materials</th>
                <th>Status</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="run in productionRuns" :key="run.id">
                <td class="fw-semibold">
                  {{ run.run_number }}
                </td>

                <td>{{ formatDate(run.production_date) }}</td>

                <td>{{ run.planned_output }}</td>

                <td>{{ run.actual_output ?? "-" }}</td>

                <td>
                  {{ run.consumptions?.length ?? "-" }}
                </td>

                <td>
                  <span class="badge" :class="statusClass(run.status)">
                    {{ run.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- New Production Modal -->
    <div v-if="showModal" class="production-overlay">
      <div class="production-modal">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h5 class="fw-bold mb-1">Start Production</h5>
            <p class="text-muted small mb-0">
              Create a manufacturing run using an existing BOM.
            </p>
          </div>

          <button
            type="button"
            class="btn-close"
            @click="showModal = false"
          ></button>
        </div>

        <form @submit.prevent="createProductionRun">
          <!-- BOM Selection -->
          <div class="mb-3">
            <label class="form-label fw-semibold"> Bill of Materials </label>

            <select v-model="form.bom_id" class="form-select" required>
              <option value="" disabled>Select BOM</option>

              <option v-for="bom in boms" :key="bom.id" :value="bom.id">
                {{ bom.product_name }} — {{ bom.name }}
              </option>
            </select>
          </div>

          <!-- Planned Output -->
          <div class="mb-3">
            <label class="form-label fw-semibold">
              Planned Output (Packets)
            </label>

            <input
              v-model="form.planned_output"
              type="number"
              min="0.001"
              step="0.001"
              class="form-control"
              placeholder="Enter planned quantity"
              required
            />
          </div>

          <!-- Material Preview -->
          <div v-if="plannedMaterials.length" class="mb-4">
            <h6 class="fw-bold mb-3">Estimated Material Requirements</h6>

            <div class="table-responsive">
              <table class="table table-sm align-middle">
                <thead class="table-light">
                  <tr>
                    <th>Material</th>
                    <th>Required Quantity</th>
                  </tr>
                </thead>

                <tbody>
                  <tr
                    v-for="material in plannedMaterials"
                    :key="material.material_item_id"
                  >
                    <td>{{ material.material_name }}</td>
                    <td>
                      {{ material.required_quantity }}
                      {{ material.unit }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <p class="text-muted small mb-0">
              These quantities are calculated from the selected BOM.
            </p>
          </div>

          <!-- Modal Error -->
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
              Cancel
            </button>

            <button
              type="submit"
              class="btn btn-success"
              :disabled="
                saving ||
                !form.bom_id ||
                !form.planned_output ||
                Number(form.planned_output) <= 0
              "
            >
              {{ saving ? "Creating..." : "Create Production Run" }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.production-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  z-index: 1050;
}

.production-modal {
  background: white;
  color: #212529;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  border-radius: 12px;
  padding: 24px;
}

.production-modal .form-label {
  color: #343a40;
  font-size: 14px;
}
</style>
