import { computed } from "vue";
import { useI18n } from "vue-i18n";

export type AppLocale =
  | "he"
  | "en"
  | "es";

const SUPPORTED_LOCALES: AppLocale[] = [
  "he",
  "en",
  "es",
];

export function useLocale() {
  const {
    locale,
    t,
  } = useI18n();

  const isRTL = computed(
    () =>
      locale.value === "he"
  );

  const dir = computed(
    () =>
      isRTL.value
        ? "rtl"
        : "ltr"
  );

  function setLanguage(
    lang: AppLocale
  ) {
    if (
      !SUPPORTED_LOCALES.includes(
        lang
      )
    ) {
      return;
    }

    locale.value = lang;

    localStorage.setItem(
      "app-language",
      lang
    );

    document.documentElement.setAttribute(
      "dir",
      lang === "he"
        ? "rtl"
        : "ltr"
    );

    document.documentElement.setAttribute(
      "lang",
      lang
    );
  }

  return {
    locale,
    isRTL,
    dir,
    setLanguage,
    t,
  };
}
