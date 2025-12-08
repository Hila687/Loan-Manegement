<template>
  <div :dir="dir" class="flex min-h-screen bg-gradient-to-br from-[#F7F8FC] to-[#EEF2F6]">
    <!-- Desktop Sidebar Navigation -->
    <nav
      class="hidden lg:flex lg:flex-col w-64 xl:w-72 bg-white/80 backdrop-blur-xl border-r border-gray-200/50 min-h-screen z-40 shadow-sm"
    >
      <!-- Sidebar logo / title -->
      <div class="p-6 xl:p-8 border-b border-gray-200/50">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-[#007AFF] to-[#0051D5] flex items-center justify-center shadow-lg shadow-[#007AFF]/20">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-3m0 0l7-4 7 4M5 9v10a1 1 0 001 1h12a1 1 0 001-1V9"/>
            </svg>
          </div>
          <h1 class="text-xl xl:text-2xl font-bold bg-gradient-to-r from-[#007AFF] to-[#0051D5] bg-clip-text text-transparent">
            {{ t("app.title") }}
          </h1>
        </div>
      </div>

      <!-- Sidebar navigation items -->
      <div class="flex-1 overflow-y-auto p-4 xl:p-6 space-y-1.5">
        <router-link
          to="/"
          class="flex items-center gap-3 px-4 py-3 xl:py-3.5 rounded-xl transition-all duration-200 group"
          :class="
            route.path === '/'
              ? 'bg-gradient-to-r from-[#007AFF] to-[#0051D5] text-white shadow-lg shadow-[#007AFF]/30'
              : 'text-gray-600 hover:bg-gray-50 hover:text-[#007AFF]'
          "
        >
          <svg class="w-5 h-5 xl:w-6 xl:h-6 transition-transform group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-3m0 0l7-4 7 4M5 9v10a1 1 0 001 1h12a1 1 0 001-1V9"/>
          </svg>
          <span class="font-medium text-sm xl:text-base">{{ t("nav.home") }}</span>
        </router-link>

        <router-link
          to="/loans/new"
          class="flex items-center gap-3 px-4 py-3 xl:py-3.5 rounded-xl transition-all duration-200 group"
          :class="
            route.path === '/loans/new'
              ? 'bg-gradient-to-r from-[#007AFF] to-[#0051D5] text-white shadow-lg shadow-[#007AFF]/30'
              : 'text-gray-600 hover:bg-gray-50 hover:text-[#007AFF]'
          "
        >
          <svg class="w-5 h-5 xl:w-6 xl:h-6 transition-transform group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          <span class="font-medium text-sm xl:text-base">{{ t("nav.createLoan") }}</span>
        </router-link>

        <router-link
          to="/loans"
          class="flex items-center gap-3 px-4 py-3 xl:py-3.5 rounded-xl transition-all duration-200 group"
          :class="
            route.path === '/loans'
              ? 'bg-gradient-to-r from-[#007AFF] to-[#0051D5] text-white shadow-lg shadow-[#007AFF]/30'
              : 'text-gray-600 hover:bg-gray-50 hover:text-[#007AFF]'
          "
        >
          <svg class="w-5 h-5 xl:w-6 xl:h-6 transition-transform group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7 7h3m-3 5h2m-2 5h8"/>
          </svg>
          <span class="font-medium text-sm xl:text-base">{{ t("nav.activeLoans") }}</span>
        </router-link>

        <router-link
          to="/dashboard"
          class="flex items-center gap-3 px-4 py-3 xl:py-3.5 rounded-xl transition-all duration-200 group"
          :class="
            route.path === '/dashboard'
              ? 'bg-gradient-to-r from-[#007AFF] to-[#0051D5] text-white shadow-lg shadow-[#007AFF]/30'
              : 'text-gray-600 hover:bg-gray-50 hover:text-[#007AFF]'
          "
        >
          <svg class="w-5 h-5 xl:w-6 xl:h-6 transition-transform group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm6 0v-10a2 2 0 00-2-2h-2a2 2 0 00-2 2v10m6 0a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2h-2a2 2 0 00-2 2"/>
          </svg>
          <span class="font-medium text-sm xl:text-base">{{ t("nav.dashboard") }}</span>
        </router-link>
      </div>
    </nav>

    <!-- Main content area -->
    <div class="flex-1 flex flex-col min-h-0 overflow-hidden">
      <!-- Desktop / tablet header -->
      <header class="hidden lg:flex items-center justify-between bg-white/60 backdrop-blur-xl px-6 xl:px-8 py-4 xl:py-5 border-b border-gray-200/50 shadow-sm">
        <div class="flex items-center gap-4">
          <button
            v-if="showBackButton"
            @click="goBack"
            class="w-10 h-10 xl:w-11 xl:h-11 flex items-center justify-center rounded-xl hover:bg-gray-100 transition-all duration-200 active:scale-95"
          >
            <svg class="h-5 w-5 xl:h-6 xl:w-6" fill="none" stroke="currentColor">
              <path d="M15 19l-7-7 7-7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>

          <div :class="locale === 'he' ? 'text-right' : 'text-left'">
            <h1 v-if="title" class="text-xl xl:text-2xl font-bold text-[#111827]">
              {{ title }}
            </h1>
            <p v-if="subtitle" class="text-sm xl:text-base text-[#6B7280] mt-0.5">
              {{ subtitle }}
            </p>
          </div>
        </div>

        <button
          v-if="showLanguageToggle"
          @click="toggleLanguage"
          class="flex items-center gap-2 px-4 py-2 xl:px-5 xl:py-2.5 rounded-xl border-2 border-[#E5E5EA] bg-white text-sm xl:text-base font-medium transition-all hover:bg-gray-50 hover:border-[#007AFF] hover:text-[#007AFF] active:scale-95"
        >
          <svg class="w-4 h-4 xl:w-5 xl:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"/>
          </svg>
          <span>{{ locale === "he" ? "EN" : "HE" }}</span>
        </button>
      </header>

      <!-- Mobile top bar -->
      <div class="lg:hidden flex items-center justify-between bg-white/90 backdrop-blur-xl border-b border-gray-200/50 px-4 py-3 sticky top-0 z-30 shadow-sm">
        <div class="flex items-center gap-3 flex-1 min-w-0">
          <button
            v-if="showBackButton"
            @click="goBack"
            class="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-gray-100 transition-all active:scale-95 flex-shrink-0"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor">
              <path d="M15 19l-7-7 7-7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <h2 v-if="title" class="text-base font-bold text-gray-900 truncate">
            {{ title }}
          </h2>
        </div>

        <div class="flex items-center gap-2 flex-shrink-0">
          <button
            v-if="showLanguageToggle"
            @click="toggleLanguage"
            class="px-3 py-1.5 rounded-lg border border-[#E5E5EA] bg-white text-xs font-medium text-gray-700 hover:bg-gray-50 hover:border-[#007AFF] transition-all active:scale-95"
          >
            {{ locale === "he" ? "EN" : "HE" }}
          </button>
          <button
            @click="mobileMenuOpen = !mobileMenuOpen"
            class="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-gray-100 transition-all active:scale-95"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Main page content -->
      <main class="flex-1 min-h-0 overflow-y-auto px-4 py-4 sm:px-6 sm:py-6 lg:px-8 lg:py-8 xl:px-10 xl:py-10">
        <div class="w-full mx-auto" :class="maxWidthClass">
          <slot />
        </div>
      </main>

      <!-- Desktop / tablet footer -->
      <footer
        v-if="$slots.footer || footerText"
        class="hidden lg:block px-6 xl:px-8 py-4 xl:py-5 bg-white/60 backdrop-blur-xl border-t border-gray-200/50"
      >
        <div class="w-full mx-auto" :class="maxWidthClass">
          <slot name="footer">
            <p v-if="footerText" class="text-xs xl:text-sm text-center text-[#6B7280]">
              {{ footerText }}
            </p>
          </slot>
        </div>
      </footer>

      <!-- Mobile / tablet footer -->
      <footer
        v-if="$slots.footer || footerText"
        class="lg:hidden px-4 py-3 bg-white/95 backdrop-blur-xl border-t border-gray-200/60"
      >
        <div class="w-full mx-auto" :class="maxWidthClass">
          <slot name="footer">
            <p v-if="footerText" class="text-xs text-center text-[#6B7280]">
              {{ footerText }}
            </p>
          </slot>
        </div>
      </footer>
    </div>

    <!-- Mobile menu overlay -->
    <transition name="fade">
      <div
        v-if="mobileMenuOpen"
        class="lg:hidden fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
        @click="mobileMenuOpen = false"
      />
    </transition>

    <!-- Mobile slide-out menu -->
    <transition name="slide">
      <div
        v-if="mobileMenuOpen"
        class="lg:hidden fixed right-0 top-0 bottom-0 w-72 sm:w-80 bg-white shadow-2xl z-50"
      >
        <div class="p-6 border-b border-gray-200/50 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-[#007AFF] to-[#0051D5] flex items-center justify-center shadow-lg shadow-[#007AFF]/20">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-3m0 0l7-4 7 4M5 9v10a1 1 0 001 1h12a1 1 0 001-1V9"/>
              </svg>
            </div>
            <h1 class="text-lg font-bold bg-gradient-to-r from-[#007AFF] to-[#0051D5] bg-clip-text text-transparent">
              {{ t("app.title") }}
            </h1>
          </div>
          <button
            @click="mobileMenuOpen = false"
            class="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-gray-100 transition-all active:scale-95"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <div class="p-4 space-y-1.5 overflow-y-auto" style="max-height: calc(100vh - 100px)">
          <router-link
            to="/"
            class="flex items-center gap-3 px-4 py-3.5 rounded-xl transition-all duration-200 group"
            :class="
              route.path === '/'
                ? 'bg-gradient-to-r from-[#007AFF] to-[#0051D5] text-white shadow-lg shadow-[#007AFF]/30'
                : 'text-gray-600 hover:bg-gray-50 hover:text-[#007AFF]'
            "
            @click="mobileMenuOpen = false"
          >
            <svg class="w-5 h-5 transition-transform group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-3m0 0l7-4 7 4M5 9v10a1 1 0 001 1h12a1 1 0 001-1V9"/>
            </svg>
            <span class="font-medium">{{ t("nav.home") }}</span>
          </router-link>

          <router-link
            to="/loans/new"
            class="flex items-center gap-3 px-4 py-3.5 rounded-xl transition-all duration-200 group"
            :class="
              route.path === '/loans/new'
                ? 'bg-gradient-to-r from-[#007AFF] to-[#0051D5] text-white shadow-lg shadow-[#007AFF]/30'
                : 'text-gray-600 hover:bg-gray-50 hover:text-[#007AFF]'
            "
            @click="mobileMenuOpen = false"
          >
            <svg class="w-5 h-5 transition-transform group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            <span class="font-medium">{{ t("nav.createLoan") }}</span>
          </router-link>

          <router-link
            to="/loans"
            class="flex items-center gap-3 px-4 py-3.5 rounded-xl transition-all duration-200 group"
            :class="
              route.path === '/loans'
                ? 'bg-gradient-to-r from-[#007AFF] to-[#0051D5] text-white shadow-lg shadow-[#007AFF]/30'
                : 'text-gray-600 hover:bg-gray-50 hover:text-[#007AFF]'
            "
            @click="mobileMenuOpen = false"
          >
            <svg class="w-5 h-5 transition-transform group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7 7h3m-3 5h2m-2 5h8"/>
            </svg>
            <span class="font-medium">{{ t("nav.activeLoans") }}</span>
          </router-link>

          <router-link
            to="/dashboard"
            class="flex items-center gap-3 px-4 py-3.5 rounded-xl transition-all duration-200 group"
            :class="
              route.path === '/dashboard'
                ? 'bg-gradient-to-r from-[#007AFF] to-[#0051D5] text-white shadow-lg shadow-[#007AFF]/30'
                : 'text-gray-600 hover:bg-gray-50 hover:text-[#007AFF]'
            "
            @click="mobileMenuOpen = false"
          >
            <svg class="w-5 h-5 transition-transform group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm6 0v-10a2 2 0 00-2-2h-2a2 2 0 00-2 2v10m6 0a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2h-2a2 2 0 00-2 2"/>
            </svg>
            <span class="font-medium">{{ t("nav.dashboard") }}</span>
          </router-link>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
import { useLocale } from "../composables/useLocale";

const props = defineProps({
  title: String,
  subtitle: String,
  showLanguageToggle: { type: Boolean, default: true },
  showBackButton: { type: Boolean, default: true },
  footerText: String,
  maxWidth: { type: String, default: "4xl" },
});

const { t } = useI18n();
const { locale, dir, setLanguage } = useLocale();
const route = useRoute();

const mobileMenuOpen = ref(false);

const maxWidthClass = computed(() => {
  const widths = {
    full: "max-w-[1600px]",
    "7xl": "max-w-7xl",
    "6xl": "max-w-6xl",
    "5xl": "max-w-5xl",
    "4xl": "max-w-4xl",
    "3xl": "max-w-3xl",
    "2xl": "max-w-2xl",
  };
  return widths[props.maxWidth as keyof typeof widths] || widths["4xl"];
});

const toggleLanguage = () => {
  setLanguage(locale.value === "he" ? "en" : "he");
};

const goBack = () => {
  window.history.back();
};
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}
</style>
