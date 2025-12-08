<template>
  <AppLayout
    :title="t('loanList.title')"
    :subtitle="t('loanList.subtitle')"
    :show-language-toggle="true"
    max-width="full"
  >
    <div class="flex flex-col gap-4 sm:gap-5 lg:gap-6 h-full">
      <!-- ===== Search bar + refresh button (top of page) ===== -->
      <div class="flex flex-row items-stretch gap-3 sm:gap-4">
        <!-- Search input (full width) -->
        <div class="flex-1 relative min-w-0">
          <span
            :class="[
              'pointer-events-none absolute inset-y-0 flex items-center text-[#6B7280]',
              isRTL ? 'right-0 pr-4' : 'left-0 pl-4'
            ]"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <circle cx="11" cy="11" r="8" stroke-width="2" />
              <path
                d="m21 21-4.35-4.35"
                stroke-width="2"
                stroke-linecap="round"
              />
            </svg>
          </span>

          <input
            v-model="searchQuery"
            type="text"
            :placeholder="t('loanList.search.placeholder')"
            :dir="isRTL ? 'rtl' : 'ltr'"
            :class="[
              'h-11 sm:h-12 lg:h-14 w-full rounded-xl lg:rounded-2xl border-2 border-[#E5E5EA] bg-white',
              'text-sm sm:text-base font-medium text-[#111827]',
              'placeholder:text-[#6B7280] transition-all',
              'focus:border-[#007AFF] focus:outline-none focus:ring-2 focus:ring-[#007AFF]/20',
              isRTL ? 'pr-12 pl-4' : 'pl-12 pr-4'
            ]"
            @input="onSearchInput"
          />

          <!-- Clear search button -->
          <button
            v-if="searchQuery"
            @click="clearSearchInput"
            :class="[
              'absolute inset-y-0 flex items-center text-[#6B7280] hover:text-[#FF3B30] transition-colors',
              isRTL ? 'left-0 pl-4' : 'right-0 pr-4'
            ]"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <!-- Refresh button -->
        <button
          @click="fetchLoans"
          :disabled="loading"
          class="flex h-11 w-11 sm:h-12 sm:w-12 lg:h-14 lg:w-14 items-center justify-center rounded-xl lg:rounded-2xl border-2 border-[#E5E5EA] bg-white text-[#007AFF] transition-all hover:border-[#007AFF] hover:bg-[#007AFF]/5 hover:scale-110 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
          :title="t('loanList.actions.refresh')"
        >
          <svg
            :class="['w-5 h-5 sm:w-6 sm:h-6', loading && 'animate-spin']"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
        </button>
      </div>

      <!-- ===== Filter row – always column, full-width filter ===== -->
      <div class="flex flex-col gap-2">
        <p
          class="text-sm sm:text-base font-medium text-[#6B7280]"
          :class="isRTL ? 'text-right' : 'text-left'"
        >
          {{ t("loanList.filters.title") }}
        </p>

        <LoanTypeFilter
          v-model="selectedType"
          :is-rtl="isRTL"
        />
      </div>

      <!-- ===== Loan table ===== -->
      <div
        class="rounded-xl lg:rounded-2xl border-2 border-[#E5E5EA] bg-white/80 backdrop-blur-sm overflow-hidden shadow-sm hover:shadow-lg transition-shadow duration-300"
      >
        <LoanTable
          :loans="loans"
          :loading="loading"
          :isRTL="isRTL"
          :t="t"
          :empty-message="
            hasActiveFilters
              ? 'loanList.messages.noFilteredLoans'
              : 'loanList.messages.noLoans'
          "
          :empty-description="
            hasActiveFilters
              ? 'loanList.messages.noFilteredLoansDesc'
              : 'loanList.messages.noLoansDesc'
          "
          @row-click="handleLoanClick"
        />
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { onMounted, watch, computed } from "vue";
import { useRouter } from "vue-router";
import { useLocale } from "../composables/useLocale";
import { useLoans } from "../composables/useLoans";
import { useLoanFilters } from "../composables/useLoanFilters";
import AppLayout from "../components/AppLayout.vue";
import LoanTable from "../components/LoanTable.vue";
import LoanTypeFilter from "../components/LoanTypeFilter.vue";
import type { LoanListItem } from "../types/loan";

const { t, isRTL } = useLocale();
const router = useRouter();

const {
  loans,
  loading,
  error,
  hasActiveFilters: hasActiveLoansFilters,
  fetchLoans,
  setFilter
} = useLoans();

const {
  selectedType,
  searchQuery,
  hasActiveFilters: hasActiveUIFilters
} = useLoanFilters();

const hasActiveFilters = computed(
  () => hasActiveLoansFilters.value || hasActiveUIFilters.value
);

const handleLoanClick = (loan: LoanListItem) => {
  router.push(`/loans/${loan.id}`);
};

let searchTimeout: ReturnType<typeof setTimeout> | undefined;

const onSearchInput = () => {
  if (searchTimeout !== undefined) {
    clearTimeout(searchTimeout);
  }
  searchTimeout = setTimeout(() => {
    setFilter("search", searchQuery.value || undefined);
  }, 300);
};

const clearSearchInput = () => {
  searchQuery.value = "";
  setFilter("search", undefined);
};

watch(selectedType, (newType) => {
  setFilter("type", newType);
});

onMounted(() => {
  fetchLoans();
});
</script>

<style scoped>
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  transform: translateY(-10px);
  opacity: 0;
}

.slide-down-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}
</style>
