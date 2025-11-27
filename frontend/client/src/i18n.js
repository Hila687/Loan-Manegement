import { createI18n } from "vue-i18n";
import he from "./locales/he.json";
import en from "./locales/en.json";

export const i18n = createI18n({
  legacy: false,
  locale: "he",
  fallbackLocale: "en",
  messages: {
    he,
    en,
  },
});
