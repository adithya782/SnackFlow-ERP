<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold mb-1">{{ t("employees.title") }}</h3>
        <p class="text-muted mb-0">
          {{ t("employees.subtitle") }}
        </p>
      </div>

      <button
        type="button"
        class="btn btn-primary"
        @click="showForm = !showForm"
      >
        {{
          showForm
            ? t("employees.closeForm")
            : "+ " + t("employees.addEmployee")
        }}
      </button>
    </div>

    <!-- Create Employee Form -->
    <div v-if="showForm" class="card shadow-sm border-0 mb-4">
      <div class="card-body">
        <h5 class="fw-bold mb-3">{{ t("employees.createAccount") }}</h5>

        <form @submit.prevent="createEmployee">
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label">{{ t("employees.fullName") }}</label>
              <input
                v-model="form.name"
                type="text"
                class="form-control"
                :placeholder="t('employees.namePlaceholder')"
                required
              />
            </div>

            <div class="col-md-6">
              <label class="form-label">{{ t("employees.email") }}</label>
              <input
                v-model="form.email"
                type="email"
                class="form-control"
                :placeholder="t('employees.emailPlaceholder')"
                required
              />
            </div>

            <div class="col-md-6">
              <label class="form-label">{{ t("employees.password") }}</label>
              <input
                v-model="form.password"
                type="password"
                class="form-control"
                minlength="8"
                :placeholder="t('employees.passwordPlaceholder')"
                required
              />
            </div>

            <div class="col-md-6">
              <label class="form-label">{{
                t("employees.employeeRole")
              }}</label>
              <select v-model="form.role" class="form-select" required>
                <option value="" disabled>
                  {{ t("employees.selectRole") }}
                </option>
                <option value="SALESMAN">
                  {{ t("employees.roles.salesman") }}
                </option>
                <option value="PRODUCTION">
                  {{ t("employees.roles.production") }}
                </option>
                <option value="ACCOUNTANT">
                  {{ t("employees.roles.accountant") }}
                </option>
              </select>
            </div>
          </div>

          <div class="mt-3">
            <button type="submit" class="btn btn-success" :disabled="saving">
              {{
                saving ? t("employees.creating") : t("employees.createEmployee")
              }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Feedback -->
    <div v-if="message" class="alert alert-success">
      {{ message }}
    </div>

    <div v-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <!-- Employee Table -->
    <div class="card border-0 shadow-sm">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h5 class="fw-bold mb-0">{{ t("employees.employeeList") }}</h5>
          <span class="badge bg-primary">
            {{ employees.length }} {{ t("employees.total") }}
          </span>
        </div>

        <div v-if="loading" class="text-center py-4">
          {{ t("employees.loading") }}
        </div>

        <div
          v-else-if="employees.length === 0"
          class="text-center py-4 text-muted"
        >
          {{ t("employees.noEmployees") }}
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th>{{ t("employees.id") }}</th>
                <th>{{ t("employees.employee") }}</th>
                <th>{{ t("employees.email") }}</th>
                <th>{{ t("employees.role") }}</th>
                <th>{{ t("employees.status") }}</th>
                <th>{{ t("employees.action") }}</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="employee in employees" :key="employee.id">
                <td>{{ employee.id }}</td>

                <td class="fw-semibold">
                  {{ employee.name }}
                </td>

                <td>{{ employee.email }}</td>

                <td>
                  <span class="badge bg-secondary">
                    {{ formatRole(employee.role) }}
                  </span>
                </td>

                <td>
                  <span
                    class="badge"
                    :class="employee.is_active ? 'bg-success' : 'bg-danger'"
                  >
                    {{
                      employee.is_active
                        ? t("employees.active")
                        : t("employees.inactive")
                    }}
                  </span>
                </td>

                <td>
                  <button
                    v-if="employee.role !== 'ADMIN'"
                    class="btn btn-sm"
                    :class="
                      employee.is_active
                        ? 'btn-outline-danger'
                        : 'btn-outline-success'
                    "
                    :disabled="updatingId === employee.id"
                    @click="toggleStatus(employee)"
                  >
                    {{
                      updatingId === employee.id
                        ? t("employees.updating")
                        : employee.is_active
                          ? t("employees.deactivate")
                          : t("employees.activate")
                    }}
                  </button>

                  <span v-else class="text-muted small">
                    {{ t("employees.protected") }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useI18n } from "vue-i18n";
import api from "../services/api";

const { t } = useI18n();

const employees = ref([]);
const loading = ref(false);
const saving = ref(false);
const updatingId = ref(null);
const showForm = ref(false);

const message = ref("");
const error = ref("");

const form = ref({
  name: "",
  email: "",
  password: "",
  role: "",
});

function formatRole(role) {
  const translations = {
    ADMIN: "employees.roles.admin",
    SALESMAN: "employees.roles.salesman",
    PRODUCTION: "employees.roles.production",
    ACCOUNTANT: "employees.roles.accountant",
  };

  return translations[role] ? t(translations[role]) : role;
}

async function fetchEmployees() {
  loading.value = true;
  error.value = "";

  try {
    const response = await api.get("/auth/users");
    employees.value = response.data.employees || [];
  } catch (err) {
    error.value = err.response?.data?.message || t("employees.loadError");
  } finally {
    loading.value = false;
  }
}

async function createEmployee() {
  saving.value = true;
  message.value = "";
  error.value = "";

  try {
    await api.post("/auth/users", {
      name: form.value.name,
      email: form.value.email,
      password: form.value.password,
      role: form.value.role,
    });

    message.value = t("employees.createSuccess");

    form.value = {
      name: "",
      email: "",
      password: "",
      role: "",
    };

    showForm.value = false;
    await fetchEmployees();
  } catch (err) {
    error.value = err.response?.data?.message || t("employees.createError");
  } finally {
    saving.value = false;
  }
}

async function toggleStatus(employee) {
  const action = employee.is_active
    ? t("employees.deactivate").toLowerCase()
    : t("employees.activate").toLowerCase();

  if (
    !window.confirm(
      t("employees.confirmStatus", {
        action,
        name: employee.name,
      }),
    )
  ) {
    return;
  }

  updatingId.value = employee.id;
  message.value = "";
  error.value = "";

  try {
    await api.patch(`/auth/users/${employee.id}/status`, {
      is_active: !employee.is_active,
    });

    message.value = employee.is_active
      ? t("employees.deactivateSuccess")
      : t("employees.activateSuccess");

    await fetchEmployees();
  } catch (err) {
    error.value = err.response?.data?.message || t("employees.statusError");
  } finally {
    updatingId.value = null;
  }
}

onMounted(fetchEmployees);
</script>
