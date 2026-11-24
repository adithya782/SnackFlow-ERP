<template>
  <div
    class="login-page min-vh-100 d-flex align-items-center justify-content-center"
  >
    <!-- Login Card -->
    <div class="card shadow border-0 login-card">
      <div class="card-body p-4 p-md-5">
        <button
          type="button"
          class="back-home-button"
          @click="router.push('/')"
        >
          ← {{ t("login.backHome") }}
        </button>
        <!-- Language Selector -->
        <div class="login-language-switch">
          <button
            type="button"
            :class="{ active: locale === 'en' }"
            @click="changeLanguage('en')"
          >
            English
          </button>

          <button
            type="button"
            :class="{ active: locale === 'ta' }"
            @click="changeLanguage('ta')"
          >
            தமிழ்
          </button>
        </div>

        <div class="text-center mb-4">
          <h2 class="fw-bold text-success">SnackFlow ERP</h2>
          <p class="text-muted">
            {{ t("login.subtitle") }}
          </p>
        </div>

        <h4 class="fw-semibold mb-1">
          {{ t("login.welcomeBack") }}
        </h4>

        <p class="text-muted mb-4">
          {{ t("login.signInDescription") }}
        </p>

        <form @submit.prevent="login">
          <div class="mb-3">
            <label class="form-label">
              {{ t("login.email") }}
            </label>

            <input
              v-model="email"
              type="email"
              class="form-control"
              placeholder="admin@example.com"
              required
            />
          </div>

          <div class="mb-3">
            <label class="form-label">
              {{ t("login.password") }}
            </label>

            <input
              v-model="password"
              type="password"
              class="form-control"
              :placeholder="t('login.passwordPlaceholder')"
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
            {{ loading ? t("login.signingIn") : t("login.signIn") }}
          </button>
        </form>

        <p class="text-muted text-center mt-4 mb-0 small">
          SnackFlow ERP · {{ t("login.footer") }}
        </p>
      </div>
    </div>

    <!-- Welcome Animation -->
    <Transition name="welcome">
      <div v-if="showWelcome" class="welcome-overlay">
        <div class="welcome-content">
          <div class="welcome-logo">🥨</div>

          <h1 class="brand-name">SNACKFLOW</h1>

          <div class="welcome-divider"></div>

          <h2 class="welcome-message">
            <span
              v-for="(letter, index) in welcomeLetters"
              :key="index"
              class="animated-letter"
              :class="{ 'letter-space': letter === ' ' }"
              :style="{ animationDelay: `${index * 0.075}s` }"
            >
              {{ letter === " " ? "\u00A0" : letter }}
            </span>
          </h2>

          <p class="welcome-tagline">
            {{ t("login.tagline") }}
          </p>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import api from "../services/api";
import { setLanguage } from "../i18n";

const router = useRouter();
const { t, locale } = useI18n();

const email = ref("");
const password = ref("");
const loading = ref(false);
const errorMessage = ref("");
const showWelcome = ref(false);

const welcomeLetters = computed(() => {
  const text = t("login.introWelcome");

  const segmenter = new Intl.Segmenter(locale.value, {
    granularity: "grapheme",
  });

  return Array.from(segmenter.segment(text), (item) => item.segment);
});

function changeLanguage(language) {
  setLanguage(language);
}

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
    localStorage.setItem("refresh_token", data.refresh_token);
    localStorage.setItem("user", JSON.stringify(data.user));

    // Show welcome animation after successful login
    showWelcome.value = true;

    // Navigate to dashboard after animation
    setTimeout(() => {
      router.push("/dashboard");
    }, 2600);
  } catch (error) {
    errorMessage.value =
      error.response?.data?.message || t("login.connectionError");
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

/* Full-screen welcome overlay */
.welcome-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: #173b2b;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: overlayFade 2.6s ease forwards;
}

.welcome-content {
  text-align: center;
  padding: 20px;
  color: white;
}

.welcome-logo {
  font-size: 65px;
  margin-bottom: 15px;
  animation: logoAppear 0.8s ease both;
}

.brand-name {
  font-size: 42px;
  font-weight: 800;
  letter-spacing: 5px;
  color: #d5eadc;
  margin-bottom: 20px;
  animation: brandAppear 0.7s ease both;
}

.welcome-divider {
  width: 90px;
  height: 3px;
  background: #8bc49e;
  margin: 0 auto 30px;
  border-radius: 10px;
  animation: dividerExpand 0.7s ease both;
}

.welcome-message {
  font-size: 27px;
  font-weight: 700;
  letter-spacing: 2px;
  white-space: nowrap;
}

.animated-letter {
  display: inline-block;
  opacity: 0;
  transform: translateY(22px);
  animation: letterAppear 0.4s ease forwards;
}

.welcome-tagline {
  color: #b8d0c1;
  font-size: 12px;
  letter-spacing: 3px;
  margin-top: 25px;
  opacity: 0;
  animation: taglineAppear 0.7s ease 1.8s forwards;
}

/* Animations */
@keyframes logoAppear {
  from {
    opacity: 0;
    transform: scale(0.5) rotate(-20deg);
  }
  to {
    opacity: 1;
    transform: scale(1) rotate(0);
  }
}

@keyframes brandAppear {
  from {
    opacity: 0;
    transform: translateY(-15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes dividerExpand {
  from {
    width: 0;
  }
  to {
    width: 90px;
  }
}

@keyframes letterAppear {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes taglineAppear {
  to {
    opacity: 1;
  }
}

@keyframes overlayFade {
  0%,
  78% {
    opacity: 1;
  }
  100% {
    opacity: 0;
  }
}

/* Overlay transition */
.welcome-leave-active {
  transition: opacity 0.25s ease;
}

.welcome-leave-to {
  opacity: 0;
}

@media (max-width: 500px) {
  .welcome-message {
    font-size: 19px;
    letter-spacing: 1px;
  }

  .brand-name {
    font-size: 32px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .welcome-overlay,
  .welcome-overlay * {
    animation-duration: 0.01ms !important;
    animation-delay: 0ms !important;
  }
}

.login-language-switch {
  display: flex;
  justify-content: flex-end;
  gap: 4px;
  margin-bottom: 22px;
  padding: 4px;
  background: #f0f4f0;
  border-radius: 25px;
  width: fit-content;
  margin-left: auto;
}

.login-language-switch button {
  border: none;
  background: transparent;
  color: #467456;
  padding: 7px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  transition: 0.2s;
}

.login-language-switch button.active {
  background: #198754;
  color: white;
}

.login-language-switch button:hover {
  opacity: 0.85;
}

.back-home-button {
  border: none;
  background: transparent;
  color: #467456;
  font-size: 13px;
  font-weight: 600;
  padding: 5px 0;
  cursor: pointer;
  transition: 0.2s;
}

.back-home-button:hover {
  color: #173b2b;
  transform: translateX(-3px);
}
</style>
