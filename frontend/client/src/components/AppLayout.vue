<script setup>
import { useLocale } from "../composables/useLocale";
import "flatpickr/dist/flatpickr.min.css";

const props = defineProps({
  title: String,
  subtitle: String,
  showLanguageToggle: { type: Boolean, default: true },
  showBackButton: { type: Boolean, default: true },
  footerText: String,
  maxWidth: { type: String, default: "4xl" },
});

const { locale, dir, setLanguage } = useLocale();

function goBack() {
  window.history.back();
}
</script>

<template>
  <div :dir="dir" class="relative flex min-h-screen w-full flex-col bg-[#F7F8FC]">
    <header
      class="sticky top-0 flex items-center bg-[#F7F8FC]/90 p-4 pb-3 backdrop-blur-sm z-10 border-b border-[#E5E5EA]/50"
    >
      <button
        v-if="showBackButton"
        @click="goBack"
        class="size-10 flex items-center justify-center rounded-full hover:bg-black/5"
      >
        <svg class="h-6 w-6" fill="none" stroke="currentColor">
          <path
            d="M15 19l-7-7 7-7"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </button>

      <div
        class="flex-1 ml-2"
        :class="locale === 'he' ? 'text-right' : 'text-left'"
      >
        <h1 class="text-xl font-semibold">{{ title }}</h1>
        <p v-if="subtitle" class="text-sm text-[#6B7280]">
          {{ subtitle }}
        </p>
      </div>

      <div v-if="showLanguageToggle" class="flex gap-2">
        <button
          @click="setLanguage(locale === 'he' ? 'en' : 'he')"
          class="flex items-center gap-2 px-3 py-1.5 rounded-full border border-[#E5E5EA] bg-white text-xs font-medium transition-all hover:bg-gray-50 hover:border-[#007AFF]/50"
        >
          <svg
            class="w-4 h-4 text-[#007AFF]"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"
            />
          </svg>
          <span>{{ locale === "he" ? "English" : "עברית" }}</span>
        </button>
      </div>
    </header>

    <main
      class="flex-1 px-4 py-6 xl:py-8 flex items-center justify-center"
    >
      <div
        class="w-full"
        :class="maxWidth === 'full' ? 'max-w-7xl' : `max-w-${maxWidth}`"
      >
        <slot />
      </div>
    </main>

    <footer
      v-if="$slots.footer || footerText"
      class="sticky bottom-0 px-4 py-4 pt-2 bg-[#F7F8FC]/90 backdrop-blur-sm border-t border-[#E5E5EA]/50"
    >
      <div
        class="w-full"
        :class="
          maxWidth === 'full'
            ? 'max-w-7xl mx-auto'
            : `max-w-${maxWidth} mx-auto`
        "
      >
        <slot name="footer">
          <p
            v-if="footerText"
            class="text-xs text-center text-[#6B7280]"
          >
            {{ footerText }}
          </p>
        </slot>
      </div>
    </footer>
  </div>
</template>