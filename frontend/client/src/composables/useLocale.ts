import { computed } from "vue";
import { useI18n } from "vue-i18n";

export function useLocale() {
  const { locale, t } = useI18n();

  const isRTL = computed(() => locale.value === "he");
  
  const dir = computed(() => (locale.value === "he" ? "rtl" : "ltr"));

  function setLanguage(lang: string) {
    locale.value = lang;
    document.documentElement.setAttribute("dir", dir.value);
  }

  return {
    locale,
    isRTL,
    dir,
    setLanguage,
    t,
  };
}