<template>
  <AppLayout
    :title="pageTitle"
    :show-language-toggle="true"
    max-width="full"
  >
    <div class="space-y-4 sm:space-y-5">
      <section
        class="rounded-2xl border border-line bg-white p-3 shadow-sm sm:p-5"
      >
        <div class="flex flex-nowrap items-center gap-2 sm:gap-3">
          <div class="relative min-w-0 flex-1">
            <span
              :class="[
                'pointer-events-none absolute inset-y-0 flex items-center text-muted',
                isRTL ? 'right-0 pr-3.5' : 'left-0 pl-3.5',
              ]"
            >
              <svg
                class="h-5 w-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
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
              :placeholder="searchPlaceholder"
              :dir="isRTL ? 'rtl' : 'ltr'"
              :class="[
                'h-12 w-full min-w-0 rounded-xl border border-line bg-white text-sm font-medium text-ink outline-none transition placeholder:text-transparent sm:placeholder:text-muted',
                'focus:border-brand focus:ring-2 focus:ring-brand/20',
                isRTL ? 'pr-10 pl-9' : 'pl-10 pr-9',
              ]"
              @input="onSearchInput"
            />

            <button
              v-if="searchQuery"
              type="button"
              :class="[
                'absolute inset-y-0 flex items-center text-muted transition hover:text-danger',
                isRTL ? 'left-0 pl-3' : 'right-0 pr-3',
              ]"
              :aria-label="clearSearchLabel"
              @click="clearSearchInput"
            >
              <svg
                class="h-4 w-4"
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
            v-if="auth.isAdmin.value"
            type="button"
            class="inline-flex h-12 w-12 flex-none cursor-pointer items-center justify-center rounded-xl bg-brand text-white shadow-lg shadow-brand/20 transition hover:bg-brand-deep active:scale-[0.98]"
            :title="newLoanLabel"
            :aria-label="newLoanLabel"
            @click="router.push('/loans/new')"
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
                stroke-width="2.2"
                d="M12 5v14m7-7H5"
              />
            </svg>
          </button>
        </div>

        <!-- Compact mobile filter panel -->
        <div class="mt-3 sm:hidden">
          <button
            type="button"
            class="flex h-11 w-full items-center justify-between rounded-xl border border-line bg-canvas px-3 text-sm font-semibold text-ink-soft"
            @click="mobileFiltersOpen = !mobileFiltersOpen"
          >
            <span class="flex items-center gap-2">
              <svg
                class="h-4 w-4 text-muted"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M4 6h16M7 12h10m-6 6h2"
                />
              </svg>

              {{ filtersLabel }}

              <span
                v-if="activeFilterCount > 0"
                class="rounded-full bg-brand px-2 py-0.5 text-[11px] font-bold text-white"
              >
                {{ activeFilterCount }}
              </span>
            </span>

            <svg
              class="h-4 w-4 transition-transform"
              :class="mobileFiltersOpen ? 'rotate-180' : ''"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </button>

          <div
            v-if="mobileFiltersOpen"
            class="mt-2 space-y-3 rounded-xl border border-line bg-white p-3"
          >
            <label class="block">
              <span class="mb-1.5 block text-xs font-semibold text-muted">
                {{ statusFilterLabel }}
              </span>

              <select
                v-model="selectedStatus"
                class="h-11 w-full rounded-xl border border-line bg-white px-3 text-sm font-semibold text-ink outline-none focus:border-brand focus:ring-2 focus:ring-brand/20"
                @change="selectStatus(selectedStatus)"
              >
                <option
                  v-for="option in statusOptions"
                  :key="option.value"
                  :value="option.value"
                >
                  {{ option.label }} ({{ option.count }})
                </option>
              </select>
            </label>

            <label class="block">
              <span class="mb-1.5 block text-xs font-semibold text-muted">
                {{ typeFilterLabel }}
              </span>

              <select
                v-model="selectedType"
                class="h-11 w-full rounded-xl border border-line bg-white px-3 text-sm font-semibold text-ink outline-none focus:border-brand focus:ring-2 focus:ring-brand/20"
                @change="selectType(selectedType)"
              >
                <option
                  v-for="option in typeOptions"
                  :key="option.value"
                  :value="option.value"
                >
                  {{ option.label }}
                </option>
              </select>
            </label>

            <button
              v-if="hasActiveFilters"
              type="button"
              class="text-xs font-semibold text-brand"
              @click="resetUiFilters"
            >
              {{ clearFiltersLabel }}
            </button>
          </div>
        </div>

        <!-- Desktop filters -->
        <div class="mt-4 hidden gap-5 sm:grid xl:grid-cols-[1.25fr_1fr]">
          <div>
            <div class="mb-2 flex items-center justify-between gap-3">
              <p class="text-xs font-semibold uppercase tracking-wide text-muted">
                {{ statusFilterLabel }}
              </p>

              <button
                v-if="hasActiveFilters"
                type="button"
                class="cursor-pointer text-xs font-semibold text-brand transition hover:text-brand-deep"
                @click="resetUiFilters"
              >
                {{ clearFiltersLabel }}
              </button>
            </div>

            <div class="flex flex-wrap gap-2">
              <button
                v-for="option in statusOptions"
                :key="option.value"
                type="button"
                :class="[
                  'inline-flex min-h-10 cursor-pointer items-center gap-2 rounded-xl border px-3.5 py-2 text-sm font-semibold transition',
                  selectedStatus === option.value
                    ? option.activeClass
                    : 'border-line bg-white text-ink-soft hover:border-brand/40 hover:bg-surface-muted',
                ]"
                @click="selectStatus(option.value)"
              >
                <span>{{ option.label }}</span>
                <span class="rounded-full bg-black/5 px-2 py-0.5 text-[11px] font-bold">
                  {{ option.count }}
                </span>
              </button>
            </div>
          </div>

          <div>
            <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">
              {{ typeFilterLabel }}
            </p>

            <div class="flex flex-wrap gap-2">
              <button
                v-for="option in typeOptions"
                :key="option.value"
                type="button"
                :class="[
                  'min-h-10 cursor-pointer rounded-xl border px-3.5 py-2 text-sm font-semibold transition',
                  selectedType === option.value
                    ? 'border-brand bg-brand/10 text-brand'
                    : 'border-line bg-white text-ink-soft hover:border-brand/40 hover:bg-surface-muted',
                ]"
                @click="selectType(option.value)"
              >
                {{ option.label }}
              </button>
            </div>
          </div>
        </div>
      </section>

      <div class="px-1">
        <p class="text-sm font-semibold text-ink-soft">
          {{ resultsLabel }}
        </p>
      </div>

      <div
        v-if="error"
        role="alert"
        class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 sm:px-5 sm:py-4"
      >
        <div class="flex items-center justify-between gap-3">
          <p class="text-sm font-medium text-red-700">
            {{ t("loanList.messages.error") }}
          </p>

          <button
            type="button"
            class="rounded-lg border border-red-200 bg-white px-4 py-2 text-sm font-semibold text-red-700 transition hover:bg-red-100"
            @click="fetchLoans()"
          >
            {{ t("loanList.actions.retry") }}
          </button>
        </div>
      </div>

      <LoanTable
        :loans="loans"
        :loading="loading"
        :isRTL="isRTL"
        :t="t"
        :locale="locale"
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
  </AppLayout>
</template>

<script setup lang="ts">
import {
  computed,
  onMounted,
  ref,
  watch,
} from "vue";

import {
  useRoute,
  useRouter,
} from "vue-router";

import AppLayout from "../components/AppLayout.vue";
import LoanTable from "../components/LoanTable.vue";
import { useLocale } from "../composables/useLocale";
import { useLoans } from "../composables/useLoans";
import { useAuth } from "../composables/useAuth";

import {
  LoanType,
  type LoanStatus,
} from "../types/loan";


type StatusFilter =
  | "all"
  | LoanStatus;


const {
  t,
  locale,
  isRTL,
} = useLocale();

const auth = useAuth();
const router = useRouter();
const route = useRoute();

function text(
  he: string,
  en: string,
  es: string
): string {
  if (locale.value === "he") {
    return he;
  }

  if (locale.value === "es") {
    return es;
  }

  return en;
}

const isArchive =
  computed(
    () =>
      route.name === "LoanArchive" ||
      route.name === "LoanArchiveWithDetails"
  );

const openedLoanId =
  computed<string | null>(() => {
    const id = route.params.id;

    return typeof id === "string"
      ? id
      : null;
  });

const {
  loans,
  loading,
  error,
  statusCounts,
  fetchLoans,
  setFilters,
} = useLoans({
  includeCompleted:
    auth.isAdmin.value,
});

const selectedType =
  ref<LoanType | "all">(
    "all"
  );

const selectedStatus =
  ref<StatusFilter>(
    "all"
  );

const searchQuery =
  ref("");

const mobileFiltersOpen =
  ref(false);

const hasActiveFilters =
  computed(() => {
    if (searchQuery.value.trim()) {
      return true;
    }

    if (selectedType.value !== "all") {
      return true;
    }

    if (isArchive.value) {
      return false;
    }

    return selectedStatus.value !== "all";
  });

const pageTitle =
  computed(() =>
    isArchive.value
      ? text(
          "ארכיון הלוואות",
          "Loan Archive",
          "Archivo de préstamos"
        )
      : text(
          "הלוואות",
          "Loans",
          "Préstamos"
        )
  );

const searchPlaceholder =
  computed(() =>
    text(
      "חיפוש לפי שם לווה, נאמן או קהילה",
      "Search by borrower, trustee, or community",
      "Buscar por prestatario, responsable o comunidad"
    )
  );

const newLoanLabel =
  computed(() =>
    text(
      "הלוואה חדשה",
      "New loan",
      "Nuevo préstamo"
    )
  );

const statusFilterLabel =
  computed(() =>
    text(
      "מצב ההלוואה",
      "Loan status",
      "Estado del préstamo"
    )
  );

const typeFilterLabel =
  computed(() =>
    text(
      "סוג הלוואה",
      "Loan type",
      "Tipo de préstamo"
    )
  );

const filtersLabel =
  computed(() =>
    text(
      "סינון",
      "Filters",
      "Filtros"
    )
  );

const activeFilterCount =
  computed(() => {
    let count = 0;

    if (
      !isArchive.value &&
      selectedStatus.value !== "all"
    ) {
      count += 1;
    }

    if (selectedType.value !== "all") {
      count += 1;
    }

    return count;
  });

const clearFiltersLabel =
  computed(() =>
    text(
      "ניקוי מסננים",
      "Clear filters",
      "Limpiar filtros"
    )
  );

const clearSearchLabel =
  computed(() =>
    text(
      "ניקוי חיפוש",
      "Clear search",
      "Limpiar búsqueda"
    )
  );

const resultsLabel =
  computed(() => {
    const count =
      loans.value.length;

    return text(
      `${count} הלוואות מוצגות`,
      `${count} loans shown`,
      `${count} préstamos mostrados`
    );
  });

const statusOptions =
  computed(() => {
    if (isArchive.value) {
      return [
        {
          value: "CLOSED" as StatusFilter,
          label: text(
            "הסתיימו",
            "Completed",
            "Finalizados"
          ),
          count:
            statusCounts.value.CLOSED,
          activeClass:
            "border-success/30 bg-success/10 text-success-deep",
        },
      ];
    }

    const allCount =
      auth.isAdmin.value
        ? statusCounts.value.ACTIVE +
          statusCounts.value.CLOSED +
          statusCounts.value.OVERDUE
        : statusCounts.value.ACTIVE +
          statusCounts.value.OVERDUE;

    const options = [
      {
        value: "all" as StatusFilter,
        label: text(
          "כולן",
          "All",
          "Todos"
        ),
        count: allCount,
        activeClass:
          "border-violet/30 bg-violet/10 text-violet",
      },
      {
        value: "ACTIVE" as StatusFilter,
        label: text(
          "פעילות",
          "Active",
          "Activos"
        ),
        count:
          statusCounts.value.ACTIVE,
        activeClass:
          "border-brand/30 bg-brand/10 text-brand",
      },
    ];

    if (auth.isAdmin.value) {
      options.push({
        value: "CLOSED" as StatusFilter,
        label: text(
          "הסתיימו",
          "Completed",
          "Finalizados"
        ),
        count:
          statusCounts.value.CLOSED,
        activeClass:
          "border-success/30 bg-success/10 text-success-deep",
      });
    }

    options.push({
      value: "OVERDUE" as StatusFilter,
      label: text(
        "בעייתיות",
        "Needs attention",
        "Problemáticos"
      ),
      count:
        statusCounts.value.OVERDUE,
      activeClass:
        "border-danger/30 bg-danger/10 text-danger",
    });

    return options;
  });

const typeOptions =
  computed(() => [
    {
      value: "all" as const,
      label: text(
        "כל הסוגים",
        "All types",
        "Todos los tipos"
      ),
    },
    {
      value: LoanType.CHECKS,
      label: text(
        "צ׳קים",
        "Checks",
        "Cheques"
      ),
    },
    {
      value: LoanType.STANDING_ORDER,
      label: text(
        "הוראת קבע",
        "Standing order",
        "Domiciliación"
      ),
    },
  ]);

function parseStatus(
  value: unknown
): StatusFilter {
  if (
    value === "ACTIVE" ||
    value === "OVERDUE" ||
    value === "CLOSED" ||
    value === "all"
  ) {
    return value;
  }

  return "all";
}

function parseType(
  value: unknown
): LoanType | "all" {
  if (
    value === LoanType.CHECKS ||
    value === LoanType.STANDING_ORDER
  ) {
    return value;
  }

  return "all";
}

function syncFiltersFromRoute():
  void {
  selectedStatus.value =
    isArchive.value
      ? "CLOSED"
      : parseStatus(
          route.query.status
        );

  selectedType.value =
    parseType(
      route.query.type
    );

  searchQuery.value =
    typeof route.query.search === "string"
      ? route.query.search
      : "";

  setFilters({
    status:
      selectedStatus.value,
    type:
      selectedType.value,
    search:
      searchQuery.value.trim() ||
      undefined,
  });
}

function updateRouteQuery():
  void {
  router.replace({
    path:
      isArchive.value
        ? "/archive"
        : "/loans",
    query: {
      ...(selectedStatus.value !== "all"
        ? {
            status:
              selectedStatus.value,
          }
        : {}),
      ...(selectedType.value !== "all"
        ? {
            type:
              selectedType.value,
          }
        : {}),
      ...(searchQuery.value.trim()
        ? {
            search:
              searchQuery.value.trim(),
          }
        : {}),
    },
  });
}

function selectStatus(
  value: StatusFilter
): void {
  selectedStatus.value = value;

  if (isArchive.value) {
    router.push({
      path: "/loans",
      query: {
        ...(value !== "all"
          ? { status: value }
          : {}),
      },
    });

    return;
  }

  setFilters({
    status: value,
  });

  updateRouteQuery();
}

function selectType(
  value: LoanType | "all"
): void {
  selectedType.value = value;

  setFilters({
    type: value,
  });

  updateRouteQuery();
}

function onSearchInput():
  void {
  setFilters({
    search:
      searchQuery.value.trim() ||
      undefined,
  });

  updateRouteQuery();
}

function clearSearchInput():
  void {
  searchQuery.value = "";

  setFilters({
    search: undefined,
  });

  updateRouteQuery();
}

function resetUiFilters():
  void {
  searchQuery.value = "";
  selectedType.value = "all";
  selectedStatus.value =
    isArchive.value
      ? "CLOSED"
      : "all";

  setFilters({
    type: "all",
    status:
      selectedStatus.value,
    search: undefined,
  });

  updateRouteQuery();
}

function handleToggleLoan(
  loanId: string | null
): void {
  const basePath =
    isArchive.value
      ? "/archive"
      : "/loans";

  if (loanId) {
    router.push({
      path: `${basePath}/${encodeURIComponent(loanId)}`,
      query: route.query,
    });

    return;
  }

  router.push({
    path: basePath,
    query: route.query,
  });
}

watch(
  () => route.fullPath,
  () => {
    syncFiltersFromRoute();
  }
);

onMounted(async () => {
  syncFiltersFromRoute();
  await fetchLoans();
});
</script>
