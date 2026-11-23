<template>
  <div class="landing-page">
    <!-- Opening Animation -->
    <Transition name="intro">
      <div v-if="showIntro" class="intro-screen">
        <div class="intro-content">
          <div class="intro-icon">🥨</div>

          <h1 class="intro-brand">SNACKFLOW</h1>

          <div class="intro-line"></div>

          <h2 class="intro-welcome">
            <span
              v-for="(letter, index) in welcomeLetters"
              :key="index"
              :style="{ animationDelay: `${index * 0.07}s` }"
              class="intro-letter"
            >
              {{ letter === " " ? "\u00A0" : letter }}
            </span>
          </h2>

          <p class="intro-caption">MANUFACTURER EDITION</p>
        </div>
      </div>
    </Transition>

    <!-- Main Landing Page -->
    <div class="landing-content">
      <!-- Navigation -->
      <nav class="navbar">
        <div class="nav-brand">
          <span class="brand-icon">🥨</span>
          <span>SNACKFLOW</span>
        </div>

        <div class="nav-right">
          <span class="edition-label">MANUFACTURER EDITION</span>
        </div>
      </nav>

      <!-- Hero Section -->
      <section class="hero-section">
        <div class="hero-text">
          <div class="eyebrow">
            <span class="status-dot"></span>
            A SMARTER WAY TO MANAGE MANUFACTURING
          </div>

          <h1>
            Your entire business.
            <span>One connected workspace.</span>
          </h1>

          <p class="hero-description">
            From raw materials to finished products, sales to payments. Manage
            your entire manufacturing operation with one integrated workspace.
          </p>

          <button class="enter-button" @click="goToLogin">
            LET'S GET IN
            <span class="button-arrow">→</span>
          </button>

          <p class="hero-note">
            Everything your business needs. All in one place.
          </p>
        </div>

        <!-- Decorative Illustration -->
        <div class="hero-visual">
          <div class="visual-circle circle-one"></div>
          <div class="visual-circle circle-two"></div>

          <div class="floating-card stock-card">
            <span class="visual-icon">📦</span>
            <div>
              <strong>Inventory</strong>
              <small>Stock management</small>
            </div>
          </div>

          <div class="main-illustration">
            <div class="illustration-top">🥨</div>
            <div class="illustration-title">SNACKFLOW</div>
            <div class="illustration-subtitle">MANUFACTURING WORKSPACE</div>

            <div class="illustration-boxes">
              <div class="product-box box-one">📦</div>
              <div class="product-box box-two">🥨</div>
              <div class="product-box box-three">📦</div>
            </div>
          </div>

          <div class="floating-card production-card">
            <span class="visual-icon">⚙️</span>
            <div>
              <strong>Production</strong>
              <small>Manufacturing control</small>
            </div>
          </div>

          <div class="floating-card sales-card">
            <span class="visual-icon">📊</span>
            <div>
              <strong>Business insights</strong>
              <small>Reports and analytics</small>
            </div>
          </div>
        </div>
      </section>

      <!-- Features -->
      <section class="features-section">
        <div class="features-heading">
          <span>ONE PLATFORM</span>
          <h2>Everything works together.</h2>
          <p>
            All your essential business operations, connected in one system.
          </p>
        </div>

        <div class="feature-grid">
          <div class="feature-card">
            <div class="feature-icon">📦</div>
            <h3>Inventory</h3>
            <p>Track stock levels, materials and finished goods.</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">⚙️</div>
            <h3>Production</h3>
            <p>Manage manufacturing runs, recipes and material usage.</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">📋</div>
            <h3>Sales</h3>
            <p>Manage customer orders, invoices and dispatches.</p>
          </div>

          <div class="feature-card">
            <div class="feature-icon">💰</div>
            <h3>Finance</h3>
            <p>Monitor payments, outstanding balances and reports.</p>
          </div>
        </div>
      </section>

      <!-- Bottom CTA -->
      <section class="bottom-cta">
        <div>
          <h2>Ready to simplify your operations?</h2>
          <p>Your business. Your people. One workspace.</p>
        </div>

        <button class="bottom-button" @click="goToLogin">
          Let's Get In <span>→</span>
        </button>
      </section>

      <!-- Footer -->
      <footer class="footer">
        <div class="footer-brand">🥨 SNACKFLOW</div>
        <p>Manufacturer Edition · Built for better business management</p>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const showIntro = ref(true);
const welcomeLetters = "WELCOME TO SNACKFLOW".split("");

onMounted(() => {
  setTimeout(() => {
    showIntro.value = false;
  }, 2400);
});

function goToLogin() {
  router.push("/login");
}
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.landing-page {
  min-height: 100vh;
  background: #f7f8f5;
  color: #173b2b;
  overflow: hidden;
}

/* INTRO ANIMATION */

.intro-screen {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: #173b2b;
  display: flex;
  align-items: center;
  justify-content: center;
}

.intro-content {
  text-align: center;
  color: white;
  padding: 20px;
}

.intro-icon {
  font-size: 65px;
  animation: iconAppear 0.7s ease both;
}

.intro-brand {
  font-size: 42px;
  font-weight: 800;
  letter-spacing: 7px;
  color: #d5eadc;
  margin: 12px 0 20px;
  animation: brandAppear 0.7s ease both;
}

.intro-line {
  width: 100px;
  height: 3px;
  background: #8bc49e;
  margin: auto auto 28px;
  animation: lineAppear 0.8s ease both;
}

.intro-welcome {
  font-size: 25px;
  font-weight: 700;
  letter-spacing: 2px;
  white-space: nowrap;
}

.intro-letter {
  display: inline-block;
  opacity: 0;
  transform: translateY(20px);
  animation: letterAppear 0.4s ease forwards;
}

.intro-caption {
  color: #b8d0c1;
  font-size: 11px;
  letter-spacing: 4px;
  margin-top: 24px;
  animation: fadeIn 0.8s ease 1.5s both;
}

.intro-leave-active {
  transition: opacity 0.55s ease;
}

.intro-leave-to {
  opacity: 0;
}

@keyframes iconAppear {
  from {
    opacity: 0;
    transform: scale(0.4) rotate(-30deg);
  }
  to {
    opacity: 1;
    transform: scale(1) rotate(0);
  }
}

@keyframes brandAppear {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes lineAppear {
  from {
    width: 0;
  }
  to {
    width: 100px;
  }
}

@keyframes letterAppear {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* NAVBAR */

.navbar {
  height: 80px;
  padding: 0 8%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e7ece7;
  background: #ffffff;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 21px;
  font-weight: 800;
  letter-spacing: 2px;
}

.brand-icon {
  font-size: 29px;
}

.edition-label {
  font-size: 11px;
  letter-spacing: 1.5px;
  color: #467456;
  font-weight: 700;
  background: #eaf3ec;
  padding: 9px 15px;
  border-radius: 30px;
}

/* HERO */

.hero-section {
  max-width: 1250px;
  min-height: 550px;
  margin: auto;
  padding: 75px 35px;
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  align-items: center;
  gap: 35px;
}

.hero-text {
  animation: heroReveal 0.9s ease both;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 1.5px;
  color: #487354;
  margin-bottom: 25px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #70a981;
}

.hero-text h1 {
  font-size: clamp(38px, 4.5vw, 61px);
  line-height: 1.12;
  font-weight: 800;
  letter-spacing: -2px;
  margin-bottom: 25px;
}

.hero-text h1 span {
  display: block;
  color: #648e70;
}

.hero-description {
  max-width: 500px;
  color: #6c7b70;
  font-size: 15px;
  line-height: 1.9;
  margin-bottom: 32px;
}

.enter-button {
  background: #173b2b;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 16px 27px;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 1.3px;
  cursor: pointer;
  transition: 0.25s;
  box-shadow: 0 8px 20px #173b2b25;
}

.enter-button:hover {
  background: #285d40;
  transform: translateY(-3px);
  box-shadow: 0 12px 25px #173b2b35;
}

.button-arrow {
  margin-left: 20px;
  font-size: 19px;
}

.hero-note {
  color: #8b9a8e;
  font-size: 12px;
  margin-top: 18px;
}

/* HERO VISUAL */

.hero-visual {
  min-height: 390px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: visualReveal 1s ease both;
}

.visual-circle {
  position: absolute;
  border-radius: 50%;
  background: #e7f0e8;
}

.circle-one {
  width: 340px;
  height: 340px;
}

.circle-two {
  width: 250px;
  height: 250px;
  background: #d5e7d9;
}

.main-illustration {
  z-index: 1;
  width: 260px;
  min-height: 270px;
  background: #173b2b;
  border-radius: 20px;
  padding: 25px 15px;
  text-align: center;
  color: white;
  box-shadow: 0 25px 50px #173b2b30;
  transform: rotate(-3deg);
}

.illustration-top {
  font-size: 42px;
}

.illustration-title {
  font-size: 21px;
  font-weight: 800;
  letter-spacing: 3px;
  margin-top: 5px;
}

.illustration-subtitle {
  color: #b8d0c1;
  font-size: 8px;
  letter-spacing: 2px;
  margin-top: 5px;
}

.illustration-boxes {
  display: flex;
  justify-content: center;
  align-items: end;
  gap: 10px;
  margin-top: 28px;
}

.product-box {
  display: grid;
  place-items: center;
  background: #d5eadc;
  color: #173b2b;
  border-radius: 8px;
  width: 58px;
  height: 65px;
  font-size: 27px;
}

.box-two {
  height: 82px;
  background: #a8cbb0;
}

.floating-card {
  position: absolute;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 12px;
  background: white;
  padding: 13px 16px;
  border-radius: 12px;
  box-shadow: 0 10px 30px #173b2b15;
  animation: float 4s ease-in-out infinite;
}

.visual-icon {
  font-size: 27px;
}

.floating-card strong,
.floating-card small {
  display: block;
}

.floating-card strong {
  font-size: 12px;
}

.floating-card small {
  color: #829187;
  font-size: 10px;
  margin-top: 4px;
}

.stock-card {
  top: 35px;
  left: 0;
}

.production-card {
  right: -5px;
  top: 125px;
  animation-delay: 0.7s;
}

.sales-card {
  bottom: 25px;
  left: 15px;
  animation-delay: 1.2s;
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes heroReveal {
  from {
    opacity: 0;
    transform: translateY(25px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes visualReveal {
  from {
    opacity: 0;
    transform: translateX(35px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* FEATURES */

.features-section {
  background: #edf3ed;
  padding: 65px 8%;
  text-align: center;
}

.features-heading > span {
  font-size: 10px;
  font-weight: 800;
  color: #648e70;
  letter-spacing: 2px;
}

.features-heading h2 {
  font-size: 30px;
  font-weight: 800;
  margin: 12px 0;
}

.features-heading p {
  color: #78887b;
  font-size: 13px;
}

.feature-grid {
  max-width: 1150px;
  margin: 38px auto 0;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
}

.feature-card {
  text-align: left;
  background: white;
  border: 1px solid #e5ece5;
  padding: 25px 20px;
  border-radius: 12px;
  transition: 0.25s;
}

.feature-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 30px #173b2b12;
}

.feature-icon {
  font-size: 30px;
  margin-bottom: 17px;
}

.feature-card h3 {
  font-size: 16px;
  font-weight: 800;
}

.feature-card p {
  color: #829187;
  font-size: 12px;
  line-height: 1.7;
  margin: 0;
}

/* BOTTOM CTA */

.bottom-cta {
  background: #173b2b;
  color: white;
  padding: 42px 8%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

.bottom-cta h2 {
  font-size: 23px;
  font-weight: 800;
}

.bottom-cta p {
  color: #b8d0c1;
  font-size: 13px;
  margin: 8px 0 0;
}

.bottom-button {
  background: #d5eadc;
  color: #173b2b;
  border: none;
  border-radius: 7px;
  padding: 14px 22px;
  font-weight: 800;
  cursor: pointer;
  transition: 0.2s;
  white-space: nowrap;
}

.bottom-button:hover {
  background: white;
  transform: translateY(-2px);
}

.bottom-button span {
  margin-left: 12px;
}

/* FOOTER */

.footer {
  background: #102c20;
  color: #b8d0c1;
  padding: 25px 8%;
  text-align: center;
}

.footer-brand {
  font-size: 15px;
  font-weight: 800;
  letter-spacing: 2px;
}

.footer p {
  font-size: 11px;
  margin: 8px 0 0;
}

/* RESPONSIVE */

@media (max-width: 900px) {
  .hero-section {
    grid-template-columns: 1fr;
    text-align: center;
    padding-top: 65px;
  }

  .hero-description {
    margin-left: auto;
    margin-right: auto;
  }

  .hero-visual {
    margin-top: 15px;
  }

  .feature-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .bottom-cta {
    flex-direction: column;
    text-align: center;
  }
}

@media (max-width: 550px) {
  .navbar {
    padding: 0 20px;
  }

  .nav-brand {
    font-size: 17px;
  }

  .edition-label {
    font-size: 8px;
    padding: 8px;
  }

  .hero-section {
    padding: 55px 20px;
  }

  .hero-text h1 {
    font-size: 39px;
  }

  .hero-visual {
    transform: scale(0.85);
    margin: -10px -25px;
  }

  .feature-grid {
    grid-template-columns: 1fr;
  }

  .features-section {
    padding: 50px 22px;
  }

  .features-heading h2 {
    font-size: 25px;
  }

  .intro-brand {
    font-size: 32px;
    letter-spacing: 5px;
  }

  .intro-welcome {
    font-size: 17px;
  }

  .intro-caption {
    font-size: 9px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .intro-screen *,
  .landing-content * {
    animation: none !important;
    transition: none !important;
  }
}
</style>
