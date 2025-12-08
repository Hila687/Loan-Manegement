<template>
  <AppLayout
    :title="t('home.title')"
    :subtitle="t('home.subtitle')"
    :show-language-toggle="true"
    :show-back-button="false"
    max-width="full"
  >
    <div class="flex flex-col gap-4 sm:gap-5 lg:gap-6 h-full">
      <!-- Welcome header -->
      <div
        class="rounded-2xl lg:rounded-3xl bg-gradient-to-br from-[#007AFF] via-[#0066CC] to-[#0051D5] p-6 sm:p-8 lg:p-10 text-white shadow-xl hover:shadow-2xl transition-shadow duration-300"
      >
        <div class="flex flex-col sm:flex-row items-start sm:items-center gap-4 sm:gap-5 mb-6">
          <div
            class="flex h-14 w-14 sm:h-16 sm:w-16 lg:h-20 lg:w-20 items-center justify-center rounded-2xl lg:rounded-3xl bg-white/20 backdrop-blur-sm shadow-lg"
          >
            <svg
              class="w-7 h-7 sm:w-8 sm:h-8 lg:w-10 lg:h-10"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M3 12l2-3m0 0l7-4 7 4M5 9v10a1 1 0 001 1h12a1 1 0 001-1V9"
              />
            </svg>
          </div>
          <div class="flex-1">
            <h2 class="text-2xl sm:text-3xl lg:text-4xl font-bold">
              {{ t("home.welcome") }}
            </h2>
            <p class="text-white/90 text-sm sm:text-base lg:text-lg mt-1.5 sm:mt-2">
              {{ t("home.welcomeMessage") }}
            </p>
          </div>
        </div>

        <!-- Quick stats -->
        <div class="grid grid-cols-2 gap-3 sm:gap-4 lg:gap-5">
          <div
            class="rounded-xl lg:rounded-2xl bg-white/10 backdrop-blur-sm p-4 sm:p-5 lg:p-6 border border-white/20 hover:bg-white/15 transition-all duration-200 hover:scale-105"
          >
            <p class="text-white/80 text-xs sm:text-sm lg:text-base font-medium mb-1 sm:mb-2">
              {{ t("home.stats.activeLoans") }}
            </p>
            <p class="text-2xl sm:text-3xl lg:text-4xl font-bold">
              {{ stats.activeLoans }}
            </p>
          </div>
          <div
            class="rounded-xl lg:rounded-2xl bg-white/10 backdrop-blur-sm p-4 sm:p-5 lg:p-6 border border-white/20 hover:bg-white/15 transition-all duration-200 hover:scale-105"
          >
            <p class="text-white/80 text-xs sm:text-sm lg:text-base font-medium mb-1 sm:mb-2">
              {{ t("home.stats.totalAmount") }}
            </p>
            <p class="text-2xl sm:text-3xl lg:text-4xl font-bold">
              {{ formatCurrency(stats.totalAmount) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Main navigation cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-5 lg:gap-6">
        <button
          @click="$router.push('/loans/new')"
          class="group relative overflow-hidden rounded-2xl lg:rounded-3xl border-2 border-[#007AFF] bg-gradient-to-br from-[#007AFF] to-[#0051D5] p-6 sm:p-8 lg:p-10 text-white transition-all duration-300 hover:shadow-2xl hover:shadow-[#007AFF]/30 hover:scale-[1.02] active:scale-[0.98]"
        >
          <div class="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16 group-hover:scale-150 transition-transform duration-500" />
          <div class="absolute bottom-0 left-0 w-24 h-24 bg-white/10 rounded-full -ml-12 -mb-12 group-hover:scale-150 transition-transform duration-500" />
          
          <div class="relative z-10">
            <div class="flex items-center justify-between mb-4 sm:mb-6">
              <div
                class="flex h-12 w-12 sm:h-14 sm:w-14 lg:h-16 lg:w-16 items-center justify-center rounded-xl lg:rounded-2xl bg-white/20 backdrop-blur-sm group-hover:scale-110 transition-transform duration-300"
              >
                <svg
                  class="w-6 h-6 sm:w-7 sm:h-7 lg:w-8 lg:h-8"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2.5"
                    d="M12 4v16m8-8H4"
                  />
                </svg>
              </div>
              <span
                class="rounded-full bg-white/20 backdrop-blur-sm px-3 sm:px-4 py-1 sm:py-1.5 text-xs sm:text-sm font-semibold border border-white/30"
              >
                {{ t("home.actions.createLoan.badge") }}
              </span>
            </div>
            <div :class="isRTL ? 'text-right' : 'text-left'">
              <h3 class="text-xl sm:text-2xl lg:text-3xl font-bold mb-2 sm:mb-3">
                {{ t("home.actions.createLoan.title") }}
              </h3>
              <p class="text-white/90 text-sm sm:text-base lg:text-lg">
                {{ t("home.actions.createLoan.description") }}
              </p>
            </div>
          </div>
        </button>

        <button
          @click="$router.push('/loans')"
          class="group relative overflow-hidden rounded-2xl lg:rounded-3xl border-2 border-[#E5E5EA] bg-white p-6 sm:p-8 lg:p-10 transition-all duration-300 hover:border-[#007AFF] hover:shadow-2xl hover:scale-[1.02] active:scale-[0.98]"
        >
          <div class="absolute top-0 right-0 w-32 h-32 bg-[#007AFF]/5 rounded-full -mr-16 -mt-16 group-hover:scale-150 transition-transform duration-500" />
          
          <div class="relative z-10">
            <div class="flex items-center justify-between mb-4 sm:mb-6">
              <div
                class="flex h-12 w-12 sm:h-14 sm:w-14 lg:h-16 lg:w-16 items-center justify-center rounded-xl lg:rounded-2xl bg-[#007AFF]/10 group-hover:bg-[#007AFF]/20 group-hover:scale-110 transition-all duration-300"
              >
                <svg
                  class="w-6 h-6 sm:w-7 sm:h-7 lg:w-8 lg:h-8 text-[#007AFF]"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2.5"
                    d="M9 12l2 2 4-4M7 7h3m-3 5h2m-2 5h8"
                  />
                </svg>
              </div>
            </div>
            <div :class="isRTL ? 'text-right' : 'text-left'">
              <h3 class="text-xl sm:text-2xl lg:text-3xl font-bold text-[#111827] mb-2 sm:mb-3">
                {{ t("home.actions.viewLoans.title") }}
              </h3>
              <p class="text-[#6B7280] text-sm sm:text-base lg:text-lg">
                {{ t("home.actions.viewLoans.description") }}
              </p>
            </div>
          </div>
        </button>
      </div>

      <!-- Secondary actions -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 lg:gap-5">
        <button
          @click="$router.push('/dashboard')"
          class="group flex items-center gap-4 rounded-xl lg:rounded-2xl border-2 border-[#E5E5EA] bg-white p-5 sm:p-6 transition-all hover:border-[#FF9500]/50 hover:shadow-lg hover:scale-[1.02] active:scale-[0.98]"
        >
          <div
            class="flex h-12 w-12 sm:h-14 sm:w-14 items-center justify-center rounded-xl lg:rounded-2xl bg-[#FF9500]/10 group-hover:bg-[#FF9500]/20 group-hover:scale-110 transition-all duration-300 flex-shrink-0"
          >
            <svg
              class="w-6 h-6 sm:w-7 sm:h-7 text-[#FF9500]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
          </div>
          <div :class="isRTL ? 'text-right' : 'text-left'" class="flex-1 min-w-0">
            <p class="text-sm sm:text-base font-semibold text-[#111827] truncate">
              {{ t("home.quickActions.dashboard") }}
            </p>
            <p class="text-xs sm:text-sm text-[#6B7280] truncate">
              {{ t("home.quickActions.dashboardDesc") }}
            </p>
          </div>
        </button>

        <button
          @click="$router.push('/reports')"
          class="group flex items-center gap-4 rounded-xl lg:rounded-2xl border-2 border-[#E5E5EA] bg-white p-5 sm:p-6 transition-all hover:border-[#34C759]/50 hover:shadow-lg hover:scale-[1.02] active:scale-[0.98]"
        >
          <div
            class="flex h-12 w-12 sm:h-14 sm:w-14 items-center justify-center rounded-xl lg:rounded-2xl bg-[#34C759]/10 group-hover:bg-[#34C759]/20 group-hover:scale-110 transition-all duration-300 flex-shrink-0"
          >
            <svg
              class="w-6 h-6 sm:w-7 sm:h-7 text-[#34C759]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <div :class="isRTL ? 'text-right' : 'text-left'" class="flex-1 min-w-0">
            <p class="text-sm sm:text-base font-semibold text-[#111827] truncate">
              {{ t("home.quickActions.reports") }}
            </p>
            <p class="text-xs sm:text-sm text-[#6B7280] truncate">
              {{ t("home.quickActions.reportsDesc") }}
            </p>
          </div>
        </button>

        <button
          @click="$router.push('/settings')"
          class="group flex items-center gap-4 rounded-xl lg:rounded-2xl border-2 border-[#E5E5EA] bg-white p-5 sm:p-6 transition-all hover:border-[#6B7280]/50 hover:shadow-lg hover:scale-[1.02] active:scale-[0.98] sm:col-span-2 lg:col-span-1"
        >
          <div
            class="flex h-12 w-12 sm:h-14 sm:w-14 items-center justify-center rounded-xl lg:rounded-2xl bg-[#6B7280]/10 group-hover:bg-[#6B7280]/20 group-hover:scale-110 transition-all duration-300 flex-shrink-0"
          >
            <svg
              class="w-6 h-6 sm:w-7 sm:h-7 text-[#6B7280]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
              />
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
          </div>
          <div :class="isRTL ? 'text-right' : 'text-left'" class="flex-1 min-w-0">
            <p class="text-sm sm:text-base font-semibold text-[#111827] truncate">
              {{ t("home.quickActions.settings") }}
            </p>
            <p class="text-xs sm:text-sm text-[#6B7280] truncate">
              {{ t("home.quickActions.settingsDesc") }}
            </p>
          </div>
        </button>
      </div>

      <!-- Recent activity placeholder -->
      <div class="rounded-2xl lg:rounded-3xl border-2 border-[#E5E5EA] bg-white/80 backdrop-blur-sm p-6 sm:p-8 lg:p-10 hover:shadow-lg transition-shadow duration-300">
        <h3 class="text-lg sm:text-xl lg:text-2xl font-bold text-[#111827] mb-6 sm:mb-8">
          {{ t("home.recentActivity.title") }}
        </h3>
        <div class="text-center py-8 sm:py-12 lg:py-16">
          <div
            class="inline-flex h-16 w-16 sm:h-20 sm:w-20 lg:h-24 lg:w-24 items-center justify-center rounded-full bg-[#6B7280]/10"
          >
            <svg
              class="w-8 h-8 sm:w-10 sm:h-10 lg:w-12 lg:h-12 text-[#6B7280]"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <p class="mt-4 sm:mt-6 text-sm sm:text-base lg:text-lg font-medium text-[#6B7280]">
            {{ t("home.recentActivity.empty") }}
          </p>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useLocale } from "../composables/useLocale";
import AppLayout from "../components/AppLayout.vue";

const { t, isRTL } = useLocale();

const stats = ref({
  activeLoans: 0,
  totalAmount: 0,
});

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat("he-IL", {
    style: "currency",
    currency: "ILS",
    minimumFractionDigits: 0,
  }).format(amount);
};

onMounted(async () => {
  stats.value = {
    activeLoans: 0,
    totalAmount: 0,
  };
});
</script>