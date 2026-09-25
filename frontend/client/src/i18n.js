import { createI18n } from "vue-i18n";

import he from "./locales/he.json";
import en from "./locales/en.json";
import es from "./locales/es.json";

const SUPPORTED_LOCALES = ["he", "en", "es"];

const savedLocale = localStorage.getItem("app-language");

const initialLocale = SUPPORTED_LOCALES.includes(savedLocale)
  ? savedLocale
  : "he";

document.documentElement.setAttribute(
  "dir",
  initialLocale === "he" ? "rtl" : "ltr"
);

document.documentElement.setAttribute(
  "lang",
  initialLocale
);

export const i18n = createI18n({
  legacy: false,
  locale: initialLocale,
  fallbackLocale: "en",
  messages: {
    he,
    en,
    es,
  },
});