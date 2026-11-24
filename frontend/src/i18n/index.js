import { createI18n } from "vue-i18n";

import en from "./locales/en.json";
import ta from "./locales/ta.json";

const savedLocale = localStorage.getItem("snackflow_language");

const i18n = createI18n({
  legacy: false,
  locale: savedLocale || "en",
  fallbackLocale: "en",
  messages: {
    en,
    ta,
  },
});

export function setLanguage(language) {
  i18n.global.locale.value = language;
  localStorage.setItem("snackflow_language", language);
}

export default i18n;
