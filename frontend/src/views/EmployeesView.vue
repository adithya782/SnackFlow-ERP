<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 class="fw-bold mb-1">Employee Management</h3>
        <p class="text-muted mb-0">
          Manage your company's employee accounts and roles.
        </p>
      </div>

      <button class="btn btn-primary" @click="showForm = !showForm">
        {{ showForm ? "Close Form" : "+ Add Employee" }}
      </button>
    </div>

    <!-- Create Employee Form -->
    <div v-if="showForm" class="card shadow-sm border-0 mb-4">
      <div class="card-body">
        <h5 class="fw-bold mb-3">Create Employee Account</h5>

        <form @submit.prevent="createEmployee">
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label">Full Name</label>
              <input
                v-model="form.name"
                type="text"
                class="form-control"
                placeholder="Enter employee name"
                required
              />
            </div>

            <div class="col-md-6">
              <label class="form-label">Email</label>
              <input
                v-model="form.email"
                type="email"
                class="form-control"
                placeholder="employee@snackflow.com"
                required
              />
            </div>

            <div class="col-md-6">
              <label class="form-label">Password</label>
              <input
                v-model="form.password"
                type="password"
                class="form-control"
                minlength="8"
                placeholder="Minimum 8 characters"
                required
              />
            </div>

            <div class="col-md-6">
              <label class="form-label">Employee Role</label>
              <select v-model="form.role" class="form-select" required>
                <option value="" disabled>Select role</option>
                <option value="SALESMAN">Salesman</option>
                <option value="PRODUCTION">Production</option>
                <option value="ACCOUNTANT">Accountant</option>
              </select>
            </div>
          </div>

          <div class="mt-3">
            <button type="submit" class="btn btn-success" :disabled="saving">
              {{ saving ? "Creating..." : "Create Employee" }}
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
          <h5 class="fw-bold mb-0">Employees</h5>
          <span class="badge bg-primary"> {{ employees.length }} Total </span>
        </div>

        <div v-if="loading" class="text-center py-4">Loading employees...</div>

        <div
          v-else-if="employees.length === 0"
          class="text-center py-4 text-muted"
        >
          No employees found.
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Employee</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Action</th>
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
                    {{ employee.role }}
                  </span>
                </td>

                <td>
                  <span
                    class="badge"
                    :class="employee.is_active ? 'bg-success' : 'bg-danger'"
                  >
                    {{ employee.is_active ? "Active" : "Inactive" }}
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
                        ? "Updating..."
                        : employee.is_active
                          ? "Deactivate"
                          : "Activate"
                    }}
                  </button>

                  <span v-else class="text-muted small"> Protected </span>
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
import api from "../services/api";

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

async function fetchEmployees() {
  loading.value = true;
  error.value = "";

  try {
    const response = await api.get("/auth/users");
    employees.value = response.data.employees || [];
  } catch (err) {
    error.value = err.response?.data?.message || "Failed to load employees.";
  } finally {
    loading.value = false;
  }
}

async function createEmployee() {
  saving.value = true;
  message.value = "";
  error.value = "";

  try {
    const response = await api.post("/auth/users", {
      name: form.value.name,
      email: form.value.email,
      password: form.value.password,
      role: form.value.role,
    });

    message.value = response.data.message;
    form.value = {
      name: "",
      email: "",
      password: "",
      role: "",
    };

    showForm.value = false;
    await fetchEmployees();
  } catch (err) {
    error.value = err.response?.data?.message || "Failed to create employee.";
  } finally {
    saving.value = false;
  }
}

async function toggleStatus(employee) {
  const action = employee.is_active ? "deactivate" : "activate";

  if (!window.confirm(`Are you sure you want to ${action} ${employee.name}?`)) {
    return;
  }

  updatingId.value = employee.id;
  message.value = "";
  error.value = "";

  try {
    const response = await api.patch(`/auth/users/${employee.id}/status`, {
      is_active: !employee.is_active,
    });

    message.value = response.data.message;
    await fetchEmployees();
  } catch (err) {
    error.value =
      err.response?.data?.message || "Failed to update employee status.";
  } finally {
    updatingId.value = null;
  }
}

onMounted(fetchEmployees);
</script>
