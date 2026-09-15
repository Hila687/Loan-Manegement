<template>
  <AppLayout
    :title="t('loanList.title')"
    :subtitle="t('loanList.subtitle')"
    :show-language-toggle="true"
    max-width="full"
  >
    <div
      class="flex h-full flex-col gap-4 sm:gap-5 lg:gap-6"
    >
      <!-- Search and refresh controls -->
      <div
        class="flex flex-row items-stretch gap-3 sm:gap-4"
      >
        <div
          class="relative min-w-0 flex-1"
        >
          <span
            :class="[
              'pointer-events-none absolute inset-y-0 flex items-center text-muted',
              isRTL
                ? 'right-0 pr-4'
                : 'left-0 pl-4',
            ]"
          >
            <svg
              class="h-5 w-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <circle
                cx="11"
                cy="11"
                r="8"
                stroke-width="2"
              />

              <path
                d="m21 21-4.35-4.35"
                stroke-width="2"
                stroke-linecap="round"
              />
            </svg>
          </span>

          <input
            v-model="searchQuery"
            type="search"
            autocomplete="off"
            :placeholder="
              t(
                'loanList.search.placeholder'
              )
            "
            :dir="
              isRTL
                ? 'rtl'
                : 'ltr'
            "
            :class="[
              'h-11 w-full rounded-xl border-2 border-line bg-white text-sm font-medium text-ink transition-all placeholder:text-muted',
              'focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/20',
              'sm:h-12 sm:text-base lg:h-14 lg:rounded-2xl',
              isRTL
                ? 'pr-12 pl-12'
                : 'pl-12 pr-12',
            ]"
            @input="
              onSearchInput
            "
          />

          <button
            v-if="
              searchQuery
            "
            type="button"
            :class="[
              'absolute inset-y-0 flex items-center text-muted transition-colors hover:text-danger',
              isRTL
                ? 'left-0 pl-4'
                : 'right-0 pr-4',
            ]"
            :aria-label="
              t(
                'common.remove'
              )
            "
            @click="
              clearSearchInput
            "
          >
            <svg
              class="h-5 w-5"
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

        <button
          type="button"
          :disabled="
            loading
          "
          class="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-xl border-2 border-line bg-white text-brand transition-all hover:border-brand hover:bg-brand/5 active:scale-95 disabled:cursor-not-allowed disabled:opacity-50 sm:h-12 sm:w-12 lg:h-14 lg:w-14 lg:rounded-2xl"
          :title="
            t(
              'loanList.actions.refresh'
            )
          "
          @click="
            fetchLoans()
          "
        >
          <svg
            :class="[
              'h-5 w-5 sm:h-6 sm:w-6',
              loading
                ? 'animate-spin'
                : '',
            ]"
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

      <!-- Loan type filter -->
      <div
        class="flex flex-col gap-2"
      >
        <p
          class="text-sm font-medium text-muted sm:text-base"
          :class="
            isRTL
              ? 'text-right'
              : 'text-left'
          "
        >
          {{
            t(
              "loanList.filters.title"
            )
          }}
        </p>

        <LoanTypeFilter
          v-model="
            selectedType
          "
          :is-rtl="
            isRTL
          "
        />
      </div>

      <!-- API error -->
      <div
        v-if="
          error
        "
        role="alert"
        class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 sm:px-5 sm:py-4"
      >
        <div
          class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
        >
          <p
            class="text-sm font-medium text-red-700"
          >
            {{
              t(
                "loanList.messages.error"
              )
            }}
          </p>

          <button
            type="button"
            class="self-start rounded-lg border border-red-200 bg-white px-4 py-2 text-sm font-semibold text-red-700 transition-colors hover:bg-red-100 sm:self-auto"
            @click="
              fetchLoans()
            "
          >
            {{
              t(
                "loanList.actions.retry"
              )
            }}
          </button>
        </div>
      </div>

      <!-- Loan table -->
      <div
        class="overflow-hidden rounded-xl border-2 border-line bg-white/80 shadow-sm backdrop-blur-sm transition-shadow duration-300 hover:shadow-lg lg:rounded-2xl"
      >
        <LoanTable
  :loans="loans"
  :loading="loading"
  :is-r-t-l="isRTL"
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
  :opened-loan-id="openedLoanId"
  @toggle-loan="handleToggleLoan"
/>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import {
  computed,
  onBeforeUnmount,
  onMounted,
  watch,
} from "vue";

import {
  useRoute,
  useRouter,
} from "vue-router";

import AppLayout
  from "../components/AppLayout.vue";

import LoanTable
  from "../components/LoanTable.vue";

import LoanTypeFilter
  from "../components/LoanTypeFilter.vue";

import {
  useLocale,
} from "../composables/useLocale";

import {
  useLoans,
} from "../composables/useLoans";

import {
  useLoanFilters,
} from "../composables/useLoanFilters";

const {
  t,
  isRTL,
} = useLocale();

const router =
  useRouter();

const route =
  useRoute();

const openedLoanId =
  computed<
    string | null
  >(() => {
    const id =
      route.params.id;

    return typeof id ===
      "string"
      ? id
      : null;
  });

const {
  loans,
  loading,
  error,
  hasActiveFilters:
    hasActiveLoanFilters,
  fetchLoans,
  setFilter,
} = useLoans();

const {
  selectedType,
  searchQuery,
  hasActiveFilters:
    hasActiveUiFilters,
} = useLoanFilters();

const hasActiveFilters =
  computed(() => {
    return (
      hasActiveLoanFilters.value ||
      hasActiveUiFilters.value
    );
  });

let searchTimeout:
  ReturnType<
    typeof setTimeout
  > | null = null;

function handleToggleLoan(
  loanId:
    string | null
): void {
  if (loanId) {
    router.push(
      `/loans/${encodeURIComponent(
        loanId
      )}`
    );

    return;
  }

  router.push(
    "/loans"
  );
}

function onSearchInput():
  void {
  if (
    searchTimeout
  ) {
    clearTimeout(
      searchTimeout
    );
  }

  searchTimeout =
    setTimeout(() => {
      const query =
        searchQuery.value
          .trim();

      setFilter(
        "search",
        query ||
          undefined
      );

      searchTimeout =
        null;
    }, 300);
}

function clearSearchInput():
  void {
  if (
    searchTimeout
  ) {
    clearTimeout(
      searchTimeout
    );

    searchTimeout =
      null;
  }

  searchQuery.value =
    "";

  setFilter(
    "search",
    undefined
  );
}

watch(
  selectedType,
  (
    newType
  ) => {
    setFilter(
      "type",
      newType
    );
  }
);

onMounted(() => {
  fetchLoans();
});

onBeforeUnmount(() => {
  if (
    searchTimeout
  ) {
    clearTimeout(
      searchTimeout
    );
  }
});
</script>

<style scoped>
@keyframes spin {
  to {
    transform: rotate(
      360deg
    );
  }
}

.animate-spin {
  animation:
    spin
    1s
    linear
    infinite;
}
</style>