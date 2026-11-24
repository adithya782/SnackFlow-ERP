<template>
  <div class="app-shell">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ 'sidebar-open': sidebarOpen }">
      <div class="brand">
        <h4>🥨 SnackFlow</h4>
        <small>{{ $t("app.subtitle") }}</small>
      </div>

      <div class="menu-label">{{ $t("layout.workspace") }}</div>

      <RouterLink to="/dashboard" class="nav-link" @click="sidebarOpen = false">
        <span>▦</span> {{ $t("layout.dashboard") }}
      </RouterLink>

      <div class="menu-label">{{ $t("layout.management") }}</div>

      <RouterLink
        v-for="item in visibleModules"
        :key="item.path"
        :to="`/modules/${item.path}`"
        class="nav-link"
        @click="sidebarOpen = false"
      >
        <span>{{ item.icon }}</span>
        {{ $t(`nav.${item.translationKey}`) }}
      </RouterLink>

      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">
            {{ user?.name?.charAt(0)?.toUpperCase() || "U" }}
          </div>

          <div>
            <strong>{{ user?.name || $t("layout.user") }}</strong>
            <small>{{ user?.role || $t("layout.employee") }}</small>
          </div>
        </div>

        <button class="logout-btn" @click="logout">
          ↪ {{ $t("layout.logout") }}
        </button>
      </div>
    </aside>

    <!-- Main area -->
    <div class="main-area">
      <header class="topbar">
        <button class="menu-toggle" @click="sidebarOpen = !sidebarOpen">
          ☰
        </button>

        <span class="topbar-title">{{ $t("app.name") }}</span>

        <div class="topbar-actions">
          <div class="language-switch">
            <button
              :class="{ active: locale === 'en' }"
              @click="changeLanguage('en')"
            >
              English
            </button>

            <button
              :class="{ active: locale === 'ta' }"
              @click="changeLanguage('ta')"
            >
              தமிழ்
            </button>
          </div>

          <span class="role-badge">
            {{ user?.role || "User" }}
          </span>
        </div>
      </header>

      <main class="page-content">
        <RouterView />
      </main>
    </div>

    <div
      v-if="sidebarOpen"
      class="sidebar-overlay"
      @click="sidebarOpen = false"
    ></div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { RouterLink, RouterView, useRouter } from "vue-router";
import { useI18n } from "vue-i18n";
import { setLanguage } from "../i18n";

const router = useRouter();
const { locale } = useI18n();

const sidebarOpen = ref(false);
const user = ref(JSON.parse(localStorage.getItem("user") || "null"));

const modules = [
  {
    name: "Items",
    translationKey: "items",
    path: "items",
    icon: "📦",
    roles: ["ADMIN"],
  },
  {
    name: "Customers",
    translationKey: "customers",
    path: "customers",
    icon: "👥",
    roles: ["ADMIN", "SALESMAN"],
  },
  {
    name: "Suppliers",
    translationKey: "suppliers",
    path: "suppliers",
    icon: "🏭",
    roles: ["ADMIN"],
  },
  {
    name: "Inventory",
    translationKey: "inventory",
    path: "inventory",
    icon: "🗃️",
    roles: ["ADMIN", "PRODUCTION"],
  },
  {
    name: "Purchases",
    translationKey: "purchases",
    path: "purchases",
    icon: "🛒",
    roles: ["ADMIN"],
  },
  {
    name: "Production",
    translationKey: "production",
    path: "production",
    icon: "⚙️",
    roles: ["ADMIN", "PRODUCTION"],
  },
  {
    name: "Sales Orders",
    translationKey: "salesOrders",
    path: "sales-orders",
    icon: "📋",
    roles: ["ADMIN", "SALESMAN"],
  },
  {
    name: "Invoices",
    translationKey: "invoices",
    path: "invoices",
    icon: "🧾",
    roles: ["ADMIN", "ACCOUNTANT"],
  },
  {
    name: "Dispatches",
    translationKey: "dispatches",
    path: "dispatches",
    icon: "🚚",
    roles: ["ADMIN"],
  },
  {
    name: "Payments",
    translationKey: "payments",
    path: "payments",
    icon: "💰",
    roles: ["ADMIN", "ACCOUNTANT"],
  },
  {
    name: "Reports",
    translationKey: "reports",
    path: "reports",
    icon: "📊",
    roles: ["ADMIN", "ACCOUNTANT"],
  },
  {
    name: "Employees",
    translationKey: "employees",
    path: "employees",
    icon: "👨‍💼",
    roles: ["ADMIN"],
  },
];

const visibleModules = computed(() => {
  const role = user.value?.role;
  return modules.filter((item) => item.roles.includes(role));
});

function changeLanguage(language) {
  setLanguage(language);
}

function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user");
  router.push("/login");
}
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: #f5f7f6;
}

.sidebar {
  width: 250px;
  background: #173b2b;
  color: white;
  position: fixed;
  inset: 0 auto 0 0;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  z-index: 1000;
}

.brand {
  padding: 25px 22px;
  border-bottom: 1px solid #ffffff20;
}

.brand h4 {
  font-weight: 700;
  margin-bottom: 3px;
}

.brand small {
  color: #b8d0c1;
}

.menu-label {
  font-size: 11px;
  letter-spacing: 1px;
  color: #a7c2b1;
  padding: 22px 22px 8px;
  font-weight: 700;
}

.nav-link {
  color: #dce9e1;
  padding: 11px 22px;
  margin: 2px 12px;
  border-radius: 7px;
  text-decoration: none;
  font-size: 14px;
  display: flex;
  gap: 12px;
  align-items: center;
}

.nav-link:hover,
.nav-link.router-link-active {
  background: #2b6348;
  color: white;
}

.sidebar-footer {
  margin-top: auto;
  padding: 18px;
  border-top: 1px solid #ffffff20;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.user-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #d5eadc;
  color: #173b2b;
  display: grid;
  place-items: center;
  font-weight: bold;
}

.user-info strong,
.user-info small {
  display: block;
}

.user-info small {
  color: #b8d0c1;
  font-size: 12px;
}

.logout-btn {
  width: 100%;
  border: 1px solid #ffffff50;
  background: transparent;
  color: white;
  padding: 8px;
  border-radius: 6px;
}

.logout-btn:hover {
  background: #ffffff15;
}

.main-area {
  margin-left: 250px;
  min-height: 100vh;
}

.topbar {
  min-height: 65px;
  background: white;
  border-bottom: 1px solid #e5e9e6;
  display: flex;
  align-items: center;
  padding: 10px 25px;
  gap: 15px;
}

.topbar-title {
  font-weight: 600;
}

.topbar-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 12px;
}

.language-switch {
  display: flex;
  align-items: center;
  border: 1px solid #dce5df;
  border-radius: 20px;
  padding: 3px;
  gap: 2px;
}

.language-switch button {
  border: none;
  background: transparent;
  padding: 6px 11px;
  border-radius: 16px;
  font-size: 12px;
  color: #52665a;
}

.language-switch button.active {
  background: #173b2b;
  color: white;
}

.role-badge {
  background: #e5f3e9;
  color: #21613b;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
}

.page-content {
  padding: 25px;
}

.menu-toggle {
  display: none;
  border: none;
  background: transparent;
  font-size: 23px;
}

.sidebar-overlay {
  display: none;
}

@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    transition: transform 0.25s;
  }

  .sidebar.sidebar-open {
    transform: translateX(0);
  }

  .main-area {
    margin-left: 0;
  }

  .menu-toggle {
    display: block;
  }

  .sidebar-overlay {
    display: block;
    position: fixed;
    inset: 0;
    background: #0008;
    z-index: 999;
  }

  .page-content {
    padding: 15px;
  }

  .topbar {
    padding: 10px 12px;
    gap: 8px;
  }

  .topbar-title {
    font-size: 14px;
  }

  .topbar-actions {
    gap: 6px;
  }

  .language-switch button {
    padding: 6px 8px;
    font-size: 11px;
  }

  .role-badge {
    padding: 5px 8px;
    font-size: 10px;
  }
}
</style>
