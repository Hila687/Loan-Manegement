<template>
  <div class="overflow-hidden rounded-2xl border border-line bg-white shadow-sm">
    <div
      v-if="loading && loans.length === 0"
      class="flex flex-col items-center justify-center px-6 py-14"
    >
      <div
        class="h-8 w-8 animate-spin rounded-full border-4 border-brand border-t-transparent"
      ></div>

      <p class="mt-4 text-sm text-muted">
        {{ t("loanList.messages.loading") }}
      </p>
    </div>

    <div
      v-else-if="!loading && loans.length === 0"
      class="flex flex-col items-center justify-center px-6 py-14 text-center"
    >
      <div
        class="flex h-12 w-12 items-center justify-center rounded-xl bg-brand/10 text-brand"
      >
        <svg
          class="h-6 w-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 12l2 2 4-4M7 7h3m-3 5h2m-2 5h8"
          />
        </svg>
      </div>

      <h3 class="mt-4 text-base font-semibold text-ink">
        {{ t(emptyMessage) }}
      </h3>

      <p class="mt-1 max-w-md text-sm text-muted">
        {{ t(emptyDescription) }}
      </p>
    </div>

    <div
      v-else
      class="divide-y divide-line"
    >
      <article
        v-for="loan in loans"
        :key="loan.id"
        class="bg-white"
      >
        <!-- Mobile loan card -->
        <button
          type="button"
          class="w-full p-4 text-start transition hover:bg-canvas/60 focus:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-brand/40 sm:hidden"
          :dir="isRTL ? 'rtl' : 'ltr'"
          :aria-expanded="expandedLoanId === loan.id"
          @click="toggleRowExpand(loan.id)"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="truncate text-lg font-bold text-ink">
                {{ loan.borrower.name || "—" }}
              </p>

              <p class="mt-1 text-xs text-muted">
                {{ formatDate(loan.startDate) }}
              </p>
            </div>

            <span
              class="inline-flex flex-shrink-0 items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold"
              :class="getStatusPillClass(loan.status)"
            >
              <span
                class="h-2 w-2 rounded-full"
                :class="getStatusDotClass(loan.status)"
              ></span>
              {{ getStatusLabel(loan.status) }}
            </span>
          </div>

          <div class="mt-4 flex items-end justify-between gap-3">
            <div>
              <p
                dir="ltr"
                class="text-2xl font-bold text-ink"
              >
                {{ formatCurrency(loan.amount) }}
              </p>

              <div class="mt-2 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-muted">
                <span class="rounded-lg bg-surface-muted px-2 py-1 font-medium text-ink-soft">
                  {{ t(getTypeLabelKey(loan.type)) }}
                </span>

                <span v-if="loan.trustee?.name" class="truncate">
                  {{ loan.trustee.name }}
                </span>
              </div>
            </div>

            <span
              class="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-surface-muted text-muted transition"
              :class="expandedLoanId === loan.id ? 'bg-brand/10 text-brand' : ''"
              aria-hidden="true"
            >
              <svg
                class="h-4 w-4 transition-transform"
                :class="expandedLoanId === loan.id ? 'rotate-180' : ''"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </span>
          </div>
        </button>

        <!-- Desktop loan row -->
        <button
          type="button"
          class="hidden w-full gap-4 p-5 text-start transition hover:bg-canvas/60 focus:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-brand/40 sm:grid sm:grid-cols-2 lg:grid-cols-[minmax(0,1.35fr)_minmax(0,1fr)_auto_minmax(0,0.9fr)_auto] lg:items-center"
          :dir="isRTL ? 'rtl' : 'ltr'"
          :aria-expanded="expandedLoanId === loan.id"
          @click="toggleRowExpand(loan.id)"
        >
          <div class="min-w-0">
            <p class="truncate text-base font-bold text-ink sm:text-lg">
              {{ loan.borrower.name || "—" }}
            </p>

            <p class="mt-1 text-xs text-muted">
              {{ formatDate(loan.startDate) }}
            </p>
          </div>

          <div class="min-w-0">
            <p class="text-xs font-medium text-muted">
              {{ t("loanList.table.trustee") }}
            </p>

            <p class="mt-1 truncate text-sm font-semibold text-ink-soft">
              {{ trusteeLabel(loan) }}
            </p>

            <p
              v-if="loan.trustee?.community && loan.trustee?.name"
              class="mt-0.5 truncate text-xs text-muted"
            >
              {{ loan.trustee.community }}
            </p>
          </div>

          <p
            dir="ltr"
            class="self-center whitespace-nowrap text-lg font-bold text-ink"
          >
            {{ formatCurrency(loan.amount) }}
          </p>

          <div class="flex min-w-0 items-center gap-2 self-center text-sm">
            <span
              class="h-2.5 w-2.5 flex-shrink-0 rounded-full"
              :class="getStatusDotClass(loan.status)"
            ></span>

            <span class="font-semibold" :class="getStatusTextClass(loan.status)">
              {{ getStatusLabel(loan.status) }}
            </span>

            <span class="text-line">·</span>

            <span class="truncate text-muted">
              {{ t(getTypeLabelKey(loan.type)) }}
            </span>
          </div>

          <div class="flex items-center justify-end self-center sm:col-start-2 sm:row-start-2 lg:col-start-auto lg:row-start-auto">
            <span
              class="flex h-9 w-9 items-center justify-center rounded-full bg-surface-muted text-muted transition"
              :class="expandedLoanId === loan.id ? 'bg-brand/10 text-brand' : ''"
              aria-hidden="true"
            >
              <svg
                class="h-4 w-4 transition-transform"
                :class="expandedLoanId === loan.id ? 'rotate-180' : ''"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </span>
          </div>
        </button>

        <div
          v-if="expandedLoanId === loan.id"
          class="border-t border-line bg-canvas/30 p-3 sm:p-5"
        >
          <div
            v-if="loadingDetails[loan.id]"
            class="flex justify-center py-8"
          >
            <div
              class="h-8 w-8 animate-spin rounded-full border-4 border-brand border-t-transparent"
            ></div>
          </div>

          <div
            v-else-if="detailsError[loan.id]"
            class="py-6 text-center"
          >
            <p class="text-sm text-red-600">
              {{ t("loanList.messages.error") }}
            </p>

            <button
              type="button"
              class="mt-3 rounded-lg bg-brand px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-deep"
              @click.stop="loadLoanDetails(loan.id, true)"
            >
              {{ t("loanList.actions.retry") }}
            </button>
          </div>

          <LoanDetailsPanel
            v-else-if="loanDetails[loan.id]"
            :loan="loanDetails[loan.id]"
            :show-status="false"
          />
        </div>
      </article>
    </div>
  </div>
</template>


<script setup lang="ts">
import {
  computed,
  reactive,
  watch,
} from "vue";

import type {
  Loan,
  LoanListItem,
  LoanStatus,
} from "../types/loan";

import {
  LoanType,
} from "../types/loan";

import LoanDetailsPanel
  from "./loan-details/LoanDetailsPanel.vue";

import loanService
  from "../services/loanService";


interface Props {
  loans: LoanListItem[];
  loading?: boolean;
  isRTL: boolean;
  locale?: string;
  t: (
    key: string
  ) => string;
  emptyMessage?: string;
  emptyDescription?: string;
  openedLoanId?:
    string | null;
}


const props =
  withDefaults(
    defineProps<Props>(),
    {
      loading: false,
      locale: "he",
      emptyMessage:
        "loanList.messages.noLoans",
      emptyDescription:
        "loanList.messages.noLoansDesc",
      openedLoanId:
        null,
    }
  );


const emit =
  defineEmits<{
    (
      event:
        "toggle-loan",
      loanId:
        string | null
    ): void;
  }>();


const expandedLoanId =
  computed(
    () =>
      props.openedLoanId
  );


const loanDetails =
  reactive<
    Record<
      string,
      Loan
    >
  >({});


const loadingDetails =
  reactive<
    Record<
      string,
      boolean
    >
  >({});


const detailsError =
  reactive<
    Record<
      string,
      boolean
    >
  >({});


async function loadLoanDetails(
  loanId: string,
  force = false
): Promise<void> {
  if (
    loanDetails[loanId] &&
    !force
  ) {
    return;
  }

  loadingDetails[loanId] =
    true;

  detailsError[loanId] =
    false;

  try {
    loanDetails[loanId] =
      await loanService
        .getLoanDetails(
          loanId
        );
  } catch {
    detailsError[loanId] =
      true;
  } finally {
    loadingDetails[loanId] =
      false;
  }
}


function toggleRowExpand(
  loanId: string
): void {
  const nextLoanId =
    expandedLoanId.value ===
    loanId
      ? null
      : loanId;

  emit(
    "toggle-loan",
    nextLoanId
  );
}


watch(
  () =>
    props.openedLoanId,
  (loanId) => {
    if (loanId) {
      loadLoanDetails(
        loanId
      );
    }
  },
  {
    immediate: true,
  }
);


function trusteeLabel(
  loan: LoanListItem
): string {
  return (
    loan.trustee?.name ||
    loan.trustee?.community ||
    "—"
  );
}


function formatCurrency(
  amount: number
): string {
  const formatterLocale =
    props.locale === "he"
      ? "he-IL"
      : props.locale === "es"
        ? "es-ES"
        : "en-US";

  return new Intl.NumberFormat(
    formatterLocale,
    {
      style: "currency",
      currency: "ILS",
      maximumFractionDigits: 2,
    }
  ).format(
    Number(
      amount || 0
    )
  );
}


function formatDate(
  value: string
): string {
  if (!value) {
    return "—";
  }

  const normalized =
    value.length === 10
      ? `${value}T00:00:00`
      : value;

  const date =
    new Date(
      normalized
    );

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return value;
  }

  const formatterLocale =
    props.locale === "he"
      ? "he-IL"
      : props.locale === "es"
        ? "es-ES"
        : "en-US";

  return date
    .toLocaleDateString(
      formatterLocale
    );
}


function getTypeLabelKey(
  type: LoanType
): string {
  return (
    type ===
    LoanType.CHECKS
      ? "loanList.types.checks"
      : "loanList.types.standingOrders"
  );
}


function getStatusLabel(
  status: LoanStatus
): string {
  if (
    props.locale === "he"
  ) {
    if (status === "OVERDUE") {
      return "בעייתית";
    }

    if (status === "CLOSED") {
      return "הסתיימה";
    }

    return "פעילה";
  }

  if (
    props.locale === "es"
  ) {
    if (status === "OVERDUE") {
      return "Problemático";
    }

    if (status === "CLOSED") {
      return "Finalizado";
    }

    return "Activo";
  }

  if (status === "OVERDUE") {
    return "Needs attention";
  }

  if (status === "CLOSED") {
    return "Completed";
  }

  return "Active";
}


function getStatusDotClass(
  status: LoanStatus
): string {
  if (status === "OVERDUE") {
    return "bg-danger";
  }

  if (status === "CLOSED") {
    return "bg-success";
  }

  return "bg-brand";
}


function getStatusTextClass(
  status: LoanStatus
): string {
  if (status === "OVERDUE") {
    return "text-danger";
  }

  if (status === "CLOSED") {
    return "text-success-deep";
  }

  return "text-brand";
}


function getStatusPillClass(
  status: LoanStatus
): string {
  if (status === "OVERDUE") {
    return "bg-danger/10 text-danger";
  }

  if (status === "CLOSED") {
    return "bg-success/10 text-success-deep";
  }

  return "bg-brand/10 text-brand";
}
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
</style>
