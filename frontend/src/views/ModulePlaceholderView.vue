<template>
  <div class="container-fluid">
    <h2 class="fw-bold">{{ moduleTitle }}</h2>

    <div class="card border-0 shadow-sm mt-4">
      <div class="card-body text-center py-5">
        <h1>🚧</h1>
        <h4 class="mt-3">{{ moduleTitle }}</h4>
        <p class="text-muted">
          This module is coming soon. We're building it step by step.
        </p>
        <RouterLink to="/dashboard" class="btn btn-success">
          Back to Dashboard
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { RouterLink, useRoute } from "vue-router";

const route = useRoute();

const moduleTitle = computed(() => {
  return String(route.params.module)
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
});
</script>
