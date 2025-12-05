<template>
  <div :dir="dir" class="flex h-screen bg-[#F7F8FC]">
    <!-- Desktop / Tablet Sidebar Navigation -->
    <nav
      class="hidden md:flex md:flex-col fixed md:relative w-64 bg-white border-r border-gray-200 h-screen z-40 md:z-auto"
      :class="{ 'md:translate-x-0': !sidebarOpen }"
    >
      <!-- Sidebar logo / title -->
      <div class="p-6 border-b border-gray-200">
        <h1 class="text-xl font-bold text-[#007AFF]">
          {{ t("app.title") }}
        </h1>
      </div>

      <!-- Sidebar navigation items -->
      <div class="flex-1 overflow-y-auto p-4 space-y-2">
        <router-link
          to="/"
          class="flex items-center gap-3 px-4 py-3 rounded-lg transition-colors"
          :class="
            $route.path === '/'
              ? 'bg-[#007AFF]/10 text-[#007AFF] font-medium'
              : 'text-gray-600 hover:bg-gray-50'
          "
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M3 12l2-3m0 0l7-4 7 4M5 9v10a1 1 0 001 1h12a1 1 0 001-1V9"
            />
          </svg>
          {{ t("nav.home") }}
        </router-link>

        <router-link
          to="/loans/new"
          class="flex items-center gap-3 px-4 py-3 rounded-lg transition-colors"
          :class="
            $route.path === '/loans/new'
              ? 'bg-[#007AFF]/10 text-[#007AFF] font-medium'
              : 'text-gray-600 hover:bg-gray-50'
          "
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 4v16m8-8H4"
            />
          </svg>
          {{ t("nav.createLoan") }}
        </router-link>

        <router-link
          to="/loans"
          class="flex items-center gap-3 px-4 py-3 rounded-lg transition-colors"
          :class="
            $route.path === '/loans'
              ? 'bg-[#007AFF]/10 text-[#007AFF] font-medium'
              : 'text-gray-600 hover:bg-gray-50'
          "
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12l2 2 4-4M7 7h3m-3 5h2m-2 5h8"
            />
          </svg>
          {{ t("nav.activeLoans") }}
        </router-link>

        <router-link
          to="/dashboard"
          class="flex items-center gap-3 px-4 py-3 rounded-lg transition-colors"
          :class="
            $route.path === '/dashboard'
              ? 'bg-[#007AFF]/10 text-[#007AFF] font-medium'
              : 'text-gray-600 hover:bg-gray-50'
          "
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm6 0v-10a2 2 0 00-2-2h-2a2 2 0 00-2 2v10m6 0a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2h-2a2 2 0 00-2 2"
            />
          </svg>
          {{ t("nav.dashboard") }}
        </router-link>
      </div>
    </nav>

    <!-- Main content area (includes header, page content and footer) -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Desktop / tablet header -->
      <header
        class="hidden md:flex items-center bg-[#F7F8FC]/90 p-4 pb-3 backdrop-blur-sm z-10 border-b border-[#E5E5EA]/50"
      >
        <!-- Back button -->
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

        <!-- Title and subtitle -->
        <div
          class="flex-1 ml-2"
          :class="locale === 'he' ? 'text-right' : 'text-left'"
        >
          <h1 v-if="title" class="text-xl font-semibold">
            {{ title }}
          </h1>
          <p v-if="subtitle" class="text-sm text-[#6B7280]">
            {{ subtitle }}
          </p>
        </div>

        <!-- Language toggle -->
        <div v-if="showLanguageToggle" class="flex gap-2">
          <button
            @click="toggleLanguage"
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

      <!-- Mobile top bar -->
      <div
        class="md:hidden flex items-center justify-between bg-white border-b border-gray-200 px-4 py-4 sticky top-0 z-30"
      >
        <div class="flex items-center gap-2">
          <button
            v-if="showBackButton"
            @click="goBack"
            class="p-2 rounded-full hover:bg-black/5"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor">
              <path
                d="M15 19l-7-7 7-7"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </button>
          <h2 v-if="title" class="text-lg font-semibold text-gray-900">
            {{ title }}
          </h2>
        </div>

        <div class="flex items-center gap-3">
          <button
            v-if="showLanguageToggle"
            @click="toggleLanguage"
            class="px-2 py-1 rounded-lg bg-gray-100 text-xs font-medium text-gray-700 hover:bg-gray-200 transition-colors"
          >
            {{ locale === "he" ? "EN" : "HE" }}
          </button>
          <button
            @click="mobileMenuOpen = !mobileMenuOpen"
            class="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"
              />
            </svg>
          </button>
        </div>
      </div>

      <!-- Main page content -->
      <main class="flex-1 overflow-y-auto pb-20 md:pb-0 px-4 py-6 xl:py-8 flex justify-center">
        <div
          class="w-full"
          :class="maxWidthClass"
        >
          <slot />
        </div>
      </main>

      <!-- Desktop / tablet footer slot -->
      <footer
        v-if="$slots.footer || footerText"
        class="hidden md:block px-4 py-4 pt-2 bg-[#F7F8FC]/90 backdrop-blur-sm border-t border-[#E5E5EA]/50"
      >
        <div class="w-full mx-auto" :class="maxWidthClass">
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

      <!-- Mobile bottom navigation -->
      <nav
        v-if="isMobileView"
        class="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-4 py-3 flex items-center justify-around"
      >
        <router-link
          to="/"
          class="flex flex-col items-center gap-1 px-3 py-2 rounded-lg transition-colors"
          :class="
            $route.path === '/'
              ? 'text-[#007AFF]'
              : 'text-gray-600 hover:bg-gray-50'
          "
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M3 12l2-3m0 0l7-4 7 4M5 9v10a1 1 0 001 1h12a1 1 0 001-1V9"
            />
          </svg>
          <span class="text-xs font-medium">{{ t("nav.home") }}</span>
        </router-link>

        <router-link
          to="/loans/new"
          class="flex flex-col items-center gap-1 px-3 py-2 rounded-lg transition-colors"
          :class="
            $route.path === '/loans/new'
              ? 'text-[#007AFF]'
              : 'text-gray-600 hover:bg-gray-50'
          "
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 4v16m8-8H4"
            />
          </svg>
          <span class="text-xs font-medium">{{ t("nav.createLoan") }}</span>
        </router-link>

        <router-link
          to="/loans"
          class="flex flex-col items-center gap-1 px-3 py-2 rounded-lg transition-colors"
          :class="
            $route.path === '/loans'
              ? 'text-[#007AFF]'
              : 'text-gray-600 hover:bg-gray-50'
          "
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12l2 2 4-4M7 7h3m-3 5h2m-2 5h8"
            />
          </svg>
          <span class="text-xs font-medium">{{ t("nav.activeLoans") }}</span>
        </router-link>

        <router-link
          to="/dashboard"
          class="flex flex-col items-center gap-1 px-3 py-2 rounded-lg transition-colors"
          :class="
            $route.path === '/dashboard'
              ? 'text-[#007AFF]'
              : 'text-gray-600 hover:bg-gray-50'
          "
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm6 0v-10a2 2 0 00-2-2h-2a2 2 0 00-2 2v10m6 0a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2h-2a2 2 0 00-2 2"
            />
          </svg>
          <span class="text-xs font-medium">{{ t("nav.dashboard") }}</span>
        </router-link>
      </nav>

      <!-- Mobile menu overlay -->
      <div
        v-if="mobileMenuOpen"
        class="md:hidden fixed inset-0 bg-black/50 z-40"
        @click="mobileMenuOpen = false"
      />

      <!-- Mobile slide-out menu -->
      <div
        class="md:hidden fixed right-0 top-0 bottom-0 w-64 bg-white shadow-xl transform transition-transform duration-300 z-50"
        :class="{ 'translate-x-full': !mobileMenuOpen }"
      >
        <div class="p-6 border-b border-gray-200 flex items-center justify-between">
          <h1 class="text-lg font-bold text-[#007AFF]">
            {{ t("app.title") }}
          </h1>
          <button
            @click="mobileMenuOpen = false"
            class="p-2 rounded-lg hover:bg-gray-100"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <div class="p-4 space-y-2">
          <router-link
            to="/"
            class="flex items-center gap-3 px-4 py-3 rounded-lg transition-colors"
            :class="
              $route.path === '/'
                ? 'bg-[#007AFF]/10 text-[#007AFF] font-medium'
                : 'text-gray-600 hover:bg-gray-50'
            "
            @click="mobileMenuOpen = false"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 12l2-3m0 0l7-4 7 4M5 9v10a1 1 0 001 1h12a1 1 0 001-1V9"
              />
            </svg>
            {{ t("nav.home") }}
          </router-link>

          <router-link
            to="/loans/new"
            class="flex items-center gap-3 px-4 py-3 rounded-lg transition-colors"
            :class="
              $route.path === '/loans/new'
                ? 'bg-[#007AFF]/10 text-[#007AFF] font-medium'
                : 'text-gray-600 hover:bg-gray-50'
            "
            @click="mobileMenuOpen = false"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 4v16m8-8H4"
              />
            </svg>
            {{ t("nav.createLoan") }}
          </router-link>

          <router-link
            to="/loans"
            class="flex items-center gap-3 px-4 py-3 rounded-lg transition-colors"
            :class="
              $route.path === '/loans'
                ? 'bg-[#007AFF]/10 text-[#007AFF] font-medium'
                : 'text-gray-600 hover:bg-gray-50'
            "
            @click="mobileMenuOpen = false"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4M7 7h3m-3 5h2m-2 5h8"
              />
            </svg>
            {{ t("nav.activeLoans") }}
          </router-link>

          <router-link
            to="/dashboard"
            class="flex items-center gap-3 px-4 py-3 rounded-lg transition-colors"
            :class="
              $route.path === '/dashboard'
                ? 'bg-[#007AFF]/10 text-[#007AFF] font-medium'
                : 'text-gray-600 hover:bg-gray-50'
            "
            @click="mobileMenuOpen = false"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm6 0v-10a2 2 0 00-2-2h-2a2 2 0 00-2 2v10m6 0a2 2 0 002 2h2a2 2 0 002-2V5a2 2 0 00-2-2h-2a2 2 0 00-2 2"
              />
            </svg>
            {{ t("nav.dashboard") }}
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useI18n } from "vue-i18n";
import { useLocale } from "../composables/useLocale";
import "flatpickr/dist/flatpickr.min.css";

const props = defineProps({
  title: String,
  subtitle: String,
  showLanguageToggle: { type: Boolean, default: true },
  showBackButton: { type: Boolean, default: true },
  footerText: String,
  maxWidth: { type: String, default: "4xl" }
});

const { t } = useI18n();
const { locale, dir, setLanguage } = useLocale();

const mobileMenuOpen = ref(false);
const sidebarOpen = ref(true);

const isMobileView = computed(() => {
  if (typeof window !== "undefined") {
    return window.innerWidth < 768;
  }
  return false;
});

// Compute max-width utility class based on prop
const maxWidthClass = computed(() => {
  if (props.maxWidth === "full") {
    return "max-w-7xl";
  }
  return `max-w-${props.maxWidth}`;
});

// Toggle language between Hebrew and English
const toggleLanguage = () => {
  setLanguage(locale.value === "he" ? "en" : "he");
};

// Go back to previous page
const goBack = () => {
  window.history.back();
};
</script>
