<script setup>
import { ref, onMounted, computed } from "vue";
import api from "../services/api";

const productionRuns = ref([]);
const boms = ref([]);
const loading = ref(true);
const saving = ref(false);
const completingRunId = ref(null);

const showModal = ref(false);
const showActualsModal = ref(false);

const error = ref("");
const modalError = ref("");

const selectedRun = ref(null);

const form = ref({
  bom_id: "",
  planned_output: "",
});

const actualForm = ref({
  actual_output: "",
  consumptions: [],
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
  modalError.value = "";

  try {
    await api.post("/production/runs", {
      bom_id: Number(form.value.bom_id),
      planned_output: Number(form.value.planned_output),
    });

    showModal.value = false;
    await fetchProduction();
  } catch (err) {
    modalError.value =
      err.response?.data?.message || "Failed to create production run.";
  } finally {
    saving.value = false;
  }
}

// Open actual production entry modal
function openActuals(run) {
  selectedRun.value = run;

  actualForm.value = {
    actual_output: run.actual_output || run.planned_output,
    consumptions: run.materials.map((material) => ({
      material_item_id: material.material_item_id,
      material_name: material.material_name,
      unit: material.unit,
      planned_quantity: material.planned_quantity,
      actual_quantity: material.actual_quantity || material.planned_quantity,
    })),
  };

  modalError.value = "";
  showActualsModal.value = true;
}

// Save actual output and material consumption
async function saveActuals() {
  if (!selectedRun.value) return;

  const output = Number(actualForm.value.actual_output);

  if (!Number.isFinite(output) || output <= 0) {
    modalError.value = "Actual output must be greater than zero.";
    return;
  }

  for (const material of actualForm.value.consumptions) {
    const quantity = Number(material.actual_quantity);

    if (!Number.isFinite(quantity) || quantity <= 0) {
      modalError.value = `Enter a valid actual quantity for ${material.material_name}.`;
      return;
    }
  }

  saving.value = true;
  modalError.value = "";

  try {
    await api.put(`/production/runs/${selectedRun.value.id}/actuals`, {
      actual_output: output,
      consumptions: actualForm.value.consumptions.map((material) => ({
        material_item_id: material.material_item_id,
        actual_quantity: Number(material.actual_quantity),
      })),
    });

    showActualsModal.value = false;
    selectedRun.value = null;

    await fetchProduction();
  } catch (err) {
    modalError.value =
      err.response?.data?.message ||
      "Failed to save actual production details.";
  } finally {
    saving.value = false;
  }
}

// Complete production and update inventory
async function completeProduction(run) {
  const confirmed = window.confirm(
    `Complete production run ${run.run_number}? This will consume raw materials and add finished goods to inventory.`,
  );

  if (!confirmed) return;

  completingRunId.value = run.id;
  error.value = "";

  try {
    const response = await api.post(`/production/runs/${run.id}/complete`);

    alert(
      response.data.message +
        "\nTotal Material Cost: ₹" +
        Number(response.data.total_material_cost).toFixed(2),
    );

    await fetchProduction();
  } catch (err) {
    error.value =
      err.response?.data?.message || "Failed to complete production.";
  } finally {
    completingRunId.value = null;
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

    <!-- Page Error -->
    <div v-if="error" class="alert alert-danger">
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
                <th>Actions</th>
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

                <td>{{ run.materials?.length ?? 0 }}</td>

                <td>
                  <span class="badge" :class="statusClass(run.status)">
                    {{ run.status }}
                  </span>
                </td>

                <td>
                  <button
                    v-if="run.status === 'PLANNED'"
                    class="btn btn-sm btn-outline-primary"
                    @click="openActuals(run)"
                  >
                    Record Actuals
                  </button>

                  <button
                    v-else-if="run.status === 'IN_PROGRESS'"
                    class="btn btn-sm btn-success"
                    :disabled="completingRunId === run.id"
                    @click="completeProduction(run)"
                  >
                    {{
                      completingRunId === run.id ? "Completing..." : "Complete"
                    }}
                  </button>

                  <span
                    v-else-if="run.status === 'COMPLETED'"
                    class="text-success small fw-semibold"
                  >
                    <i class="bi bi-check-circle"></i>
                    Completed
                  </span>

                  <span v-else class="text-muted small"> No actions </span>
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
          <div class="mb-3">
            <label class="form-label fw-semibold"> Bill of Materials </label>

            <select v-model="form.bom_id" class="form-select" required>
              <option value="" disabled>Select BOM</option>

              <option v-for="bom in boms" :key="bom.id" :value="bom.id">
                {{ bom.product_name }} — {{ bom.name }}
              </option>
            </select>
          </div>

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

          <div v-if="modalError" class="alert alert-danger">
            {{ modalError }}
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

    <!-- Actual Production Modal -->
    <div v-if="showActualsModal" class="production-overlay">
      <div class="production-modal actuals-modal">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h5 class="fw-bold mb-1">Record Actual Production</h5>
            <p class="text-muted small mb-0">
              {{ selectedRun?.run_number }}
            </p>
          </div>

          <button
            type="button"
            class="btn-close"
            @click="showActualsModal = false"
          ></button>
        </div>

        <form @submit.prevent="saveActuals">
          <div class="mb-4">
            <label class="form-label fw-semibold">
              Actual Output (Packets)
            </label>

            <input
              v-model="actualForm.actual_output"
              type="number"
              min="0.001"
              step="0.001"
              class="form-control"
              required
            />

            <small class="text-muted">
              Planned output: {{ selectedRun?.planned_output }} packets
            </small>
          </div>

          <h6 class="fw-bold mb-3">Actual Material Consumption</h6>

          <div class="table-responsive mb-3">
            <table class="table table-sm align-middle">
              <thead class="table-light">
                <tr>
                  <th>Material</th>
                  <th>Planned</th>
                  <th>Actual Quantity</th>
                </tr>
              </thead>

              <tbody>
                <tr
                  v-for="material in actualForm.consumptions"
                  :key="material.material_item_id"
                >
                  <td>
                    <div class="fw-semibold">
                      {{ material.material_name }}
                    </div>
                    <small class="text-muted">
                      {{ material.unit }}
                    </small>
                  </td>

                  <td>
                    {{ material.planned_quantity }}
                    {{ material.unit }}
                  </td>

                  <td>
                    <input
                      v-model="material.actual_quantity"
                      type="number"
                      min="0.001"
                      step="0.001"
                      class="form-control form-control-sm actual-input"
                      required
                    />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="alert alert-info small">
            Review the actual quantities carefully. Completing production will
            deduct these materials from inventory and add the actual output to
            finished goods stock.
          </div>

          <div v-if="modalError" class="alert alert-danger">
            {{ modalError }}
          </div>

          <div class="d-flex justify-content-end gap-2">
            <button
              type="button"
              class="btn btn-light"
              @click="showActualsModal = false"
            >
              Cancel
            </button>

            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? "Saving..." : "Save Actuals" }}
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

.actuals-modal {
  max-width: 760px;
}

.production-modal .form-label {
  color: #343a40;
  font-size: 14px;
}

.actual-input {
  min-width: 110px;
}
</style>
