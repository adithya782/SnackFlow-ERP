<template>
  <div
    class="login-page min-vh-100 d-flex align-items-center justify-content-center"
  >
    <div class="card shadow border-0 login-card">
      <div class="card-body p-4 p-md-5">
        <div class="text-center mb-4">
          <h2 class="fw-bold text-success">SnackFlow ERP</h2>
          <p class="text-muted">Manufacturer Management System</p>
        </div>

        <h4 class="fw-semibold mb-1">Welcome back</h4>
        <p class="text-muted mb-4">Sign in to continue</p>

        <form @submit.prevent="login">
          <div class="mb-3">
            <label class="form-label">Email address</label>
            <input
              v-model="email"
              type="email"
              class="form-control"
              placeholder="admin@example.com"
              required
            />
          </div>

          <div class="mb-3">
            <label class="form-label">Password</label>
            <input
              v-model="password"
              type="password"
              class="form-control"
              placeholder="Enter your password"
              required
            />
          </div>

          <div v-if="errorMessage" class="alert alert-danger">
            {{ errorMessage }}
          </div>

          <button
            class="btn btn-success w-100"
            type="submit"
            :disabled="loading"
          >
            {{ loading ? "Signing in..." : "Sign In" }}
          </button>
        </form>

        <p class="text-muted text-center mt-4 mb-0 small">
          SnackFlow ERP · Manufacturer Edition
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../services/api";

const router = useRouter();

const email = ref("");
const password = ref("");
const loading = ref(false);
const errorMessage = ref("");

async function login() {
  loading.value = true;
  errorMessage.value = "";

  try {
    const response = await api.post("/auth/login", {
      email: email.value,
      password: password.value,
    });

    const data = response.data;

    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("user", JSON.stringify(data.user));

    await router.push("/dashboard");
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message || "Unable to connect to the server.";
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-page {
  background: #f3f6f4;
}

.login-card {
  width: 100%;
  max-width: 440px;
  border-radius: 14px;
}
</style>
