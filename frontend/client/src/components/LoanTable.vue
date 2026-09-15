<template>
  <div
    class="bg-white rounded-xl border border-line overflow-hidden shadow-sm"
  >
    <!-- Initial loading state -->
    <div
      v-if="
        loading &&
        loans.length === 0
      "
      class="flex flex-col items-center justify-center py-14 px-6"
    >
      <div
        class="h-8 w-8 animate-spin rounded-full border-4 border-brand border-t-transparent"
      />

      <p
        class="mt-4 text-sm text-muted"
      >
        {{
          t(
            "loanList.messages.loading"
          )
        }}
      </p>
    </div>

    <!-- Empty state -->
    <div
      v-else-if="
        !loading &&
        loans.length === 0
      "
      class="flex flex-col items-center justify-center py-14 px-6 text-center"
    >
      <div
        class="w-12 h-12 rounded-xl bg-brand/10 text-brand flex items-center justify-center"
      >
        <svg
          class="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 12l2 2 4-4M7 7h3m-3 5h2m-2 5h8"
          />
        </svg>
      </div>

      <h3
        class="mt-4 text-base font-semibold text-ink"
      >
        {{
          t(
            emptyMessage
          )
        }}
      </h3>

      <p
        class="mt-1 max-w-md text-sm text-muted"
      >
        {{
          t(
            emptyDescription
          )
        }}
      </p>
    </div>

    <template v-else>
      <!-- Desktop table -->
      <div
        class="hidden md:block overflow-x-auto"
      >
        <table
          class="min-w-full divide-y divide-line"
        >
          <thead
            class="bg-canvas"
          >
            <tr>
              <th
                class="px-4 py-3 w-8"
              ></th>

              <th
                v-for="column in columns"
                :key="column.key"
                class="px-4 py-3 text-sm font-semibold text-ink-soft"
                :class="
                  isRTL
                    ? 'text-right'
                    : 'text-left'
                "
                :style="
                  column.minWidth
                    ? `min-width:${column.minWidth}`
                    : ''
                "
              >
                {{
                  column.label
                }}
              </th>
            </tr>
          </thead>

          <tbody
            class="divide-y divide-line"
          >
            <template
              v-for="loan in loans"
              :key="loan.id"
            >
              <tr
                class="hover:bg-canvas/50 transition-colors"
              >
                <!-- Expand button -->
                <td
                  class="px-4 py-4 text-center"
                >
                  <button
                    type="button"
                    class="w-8 h-8 inline-flex items-center justify-center rounded-lg text-muted hover:bg-brand/10 hover:text-brand transition-colors"
                    :title="
                      expandedLoanId ===
                      loan.id
                        ? t(
                            'loanList.hideDetails'
                          )
                        : t(
                            'loanList.showDetails'
                          )
                    "
                    @click.stop="
                      toggleRowExpand(
                        loan.id
                      )
                    "
                  >
                    <svg
                      class="w-4 h-4 transition-transform"
                      :class="
                        expandedLoanId ===
                        loan.id
                          ? 'rotate-180'
                          : ''
                      "
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
                  </button>
                </td>

                <!-- Borrower -->
                <td
                  class="px-4 py-4"
                >
                  <div
                    class="text-sm font-medium text-ink"
                  >
                    {{
                      loan.borrower.name ||
                      "—"
                    }}
                  </div>
                </td>

                <!-- Phone -->
                <td
                  class="px-4 py-4"
                >
                  <div
                    class="text-sm text-ink"
                  >
                    {{
                      formatPhone(
                        loan.borrower.phone
                      )
                    }}
                  </div>
                </td>

                <!-- Email -->
                <td
                  class="px-4 py-4 text-sm text-ink"
                >
                  {{
                    loan.borrower.email ||
                    "—"
                  }}
                </td>

                <!-- Trustee -->
                <td
                  class="px-4 py-4 text-sm text-ink"
                >
                  {{
                    loan.trustee?.name ||
                    loan.trustee?.community ||
                    "—"
                  }}
                </td>

                <!-- Amount -->
                <td
                  class="px-4 py-4"
                >
                  <span
                    class="text-sm font-medium text-ink"
                  >
                    {{
                      formatCurrency(
                        loan.amount
                      )
                    }}
                  </span>
                </td>

                <!-- Type -->
                <td
                  class="px-4 py-4"
                >
                  <span
                    class="inline-flex px-3 py-1 rounded-full text-xs font-medium"
                    :class="
                      loan.type ===
                      'checks'
                        ? 'bg-brand/10 text-brand'
                        : 'bg-warning/10 text-warning'
                    "
                  >
                    {{
                      t(
                        getTypeLabelKey(
                          loan.type
                        )
                      )
                    }}
                  </span>
                </td>

                <!-- Status -->
                <td
                  class="px-4 py-4"
                >
                  <span
                    class="inline-flex px-3 py-1 rounded-full text-xs font-semibold"
                    :class="
                      getStatusClass(
                        loan.status
                      )
                    "
                  >
                    {{
                      getStatusLabel(
                        loan.status
                      )
                    }}
                  </span>
                </td>
              </tr>

              <!-- Expanded details -->
              <tr
                v-if="
                  expandedLoanId ===
                  loan.id
                "
              >
                <td
                  :colspan="
                    columns.length + 1
                  "
                  class="px-4 py-6 bg-canvas/30"
                >
                  <div
                    v-if="
                      loadingDetails[
                        loan.id
                      ]
                    "
                    class="flex justify-center py-8"
                  >
                    <div
                      class="h-8 w-8 animate-spin rounded-full border-4 border-brand border-t-transparent"
                    />
                  </div>

                  <div
                    v-else-if="
                      detailsError[
                        loan.id
                      ]
                    "
                    class="text-center py-6"
                  >
                    <p
                      class="text-sm text-red-600"
                    >
                      {{
                        t(
                          "loanList.messages.error"
                        )
                      }}
                    </p>

                    <button
                      type="button"
                      class="mt-3 px-4 py-2 bg-brand text-white text-sm font-semibold rounded-lg hover:bg-brand-deep transition-colors"
                      @click="
                        loadLoanDetails(
                          loan.id,
                          true
                        )
                      "
                    >
                      {{
                        t(
                          "loanList.actions.retry"
                        )
                      }}
                    </button>
                  </div>

                  <LoanDetailsPanel
                    v-else-if="
                      loanDetails[
                        loan.id
                      ]
                    "
                    :loan="
                      loanDetails[
                        loan.id
                      ]
                    "
                  />
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

      <!-- Mobile cards -->
      <div
        class="md:hidden divide-y divide-line"
      >
        <article
          v-for="loan in loans"
          :key="loan.id"
          class="p-4 sm:p-5"
        >
          <button
            type="button"
            class="w-full"
            :class="
              isRTL
                ? 'text-right'
                : 'text-left'
            "
            @click="
              toggleRowExpand(
                loan.id
              )
            "
          >
            <div
              class="flex justify-between items-start gap-4"
            >
              <div
                class="min-w-0"
              >
                <div
                  class="font-semibold text-ink truncate"
                >
                  {{
                    loan.borrower.name ||
                    "—"
                  }}
                </div>

                <div
                  class="text-xs text-muted mt-1"
                >
                  {{
                    formatPhone(
                      loan.borrower.phone
                    )
                  }}
                </div>
              </div>

              <div
                class="flex-shrink-0 font-semibold text-ink"
              >
                {{
                  formatCurrency(
                    loan.amount
                  )
                }}
              </div>
            </div>

            <div
              class="mt-3 grid grid-cols-1 gap-2 text-sm text-ink-soft"
            >
              <p
                class="truncate"
              >
                {{
                  loan.borrower.email ||
                  "—"
                }}
              </p>

              <p
                class="truncate"
              >
                {{
                  loan.trustee?.name ||
                  loan.trustee?.community ||
                  "—"
                }}
              </p>
            </div>

            <div
              class="mt-3 flex flex-wrap items-center gap-2"
            >
              <span
                class="px-2.5 py-1 rounded-full text-xs font-medium"
                :class="
                  loan.type ===
                  'checks'
                    ? 'bg-brand/10 text-brand'
                    : 'bg-warning/10 text-warning'
                "
              >
                {{
                  t(
                    getTypeLabelKey(
                      loan.type
                    )
                  )
                }}
              </span>

              <span
                class="px-2.5 py-1 rounded-full text-xs font-semibold"
                :class="
                  getStatusClass(
                    loan.status
                  )
                "
              >
                {{
                  getStatusLabel(
                    loan.status
                  )
                }}
              </span>
            </div>
          </button>

          <div
            v-if="
              expandedLoanId ===
              loan.id
            "
            class="mt-4"
          >
            <div
              v-if="
                loadingDetails[
                  loan.id
                ]
              "
              class="flex justify-center py-4"
            >
              <div
                class="h-6 w-6 animate-spin rounded-full border-4 border-brand border-t-transparent"
              />
            </div>

            <div
              v-else-if="
                detailsError[
                  loan.id
                ]
              "
              class="text-center py-4"
            >
              <p
                class="text-sm text-red-600"
              >
                {{
                  t(
                    "loanList.messages.error"
                  )
                }}
              </p>

              <button
                type="button"
                class="mt-2 px-3 py-2 bg-brand text-white rounded-lg text-xs font-semibold"
                @click="
                  loadLoanDetails(
                    loan.id,
                    true
                  )
                "
              >
                {{
                  t(
                    "loanList.actions.retry"
                  )
                }}
              </button>
            </div>

            <LoanDetailsPanel
              v-else-if="
                loanDetails[
                  loan.id
                ]
              "
              :loan="
                loanDetails[
                  loan.id
                ]
              "
            />
          </div>
        </article>
      </div>
    </template>
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

const columns =
  computed(() => [
    {
      key:
        "borrower",

      label:
        props.t(
          "loanList.table.borrower"
        ),

      minWidth:
        "180px",
    },
    {
      key:
        "phone",

      label:
        props.t(
          "loanList.table.phone"
        ),

      minWidth:
        "140px",
    },
    {
      key:
        "email",

      label:
        props.t(
          "loanList.table.email"
        ),

      minWidth:
        "200px",
    },
    {
      key:
        "trustee",

      label:
        props.t(
          "loanList.table.trustee"
        ),

      minWidth:
        "180px",
    },
    {
      key:
        "amount",

      label:
        props.t(
          "loanList.table.amount"
        ),

      minWidth:
        "120px",
    },
    {
      key:
        "type",

      label:
        props.t(
          "loanList.table.type"
        ),

      minWidth:
        "140px",
    },
    {
      key:
        "status",

      label:
        props.isRTL
          ? "סטטוס"
          : "Status",

      minWidth:
        "120px",
    },
  ]);

async function loadLoanDetails(
  loanId: string,
  force = false
) {
  if (
    loanDetails[loanId] &&
    !force
  ) {
    return;
  }

  loadingDetails[
    loanId
  ] = true;

  detailsError[
    loanId
  ] = false;

  try {
    loanDetails[
      loanId
    ] =
      await loanService
        .getLoanDetails(
          loanId
        );
  } catch {
    detailsError[
      loanId
    ] = true;
  } finally {
    loadingDetails[
      loanId
    ] = false;
  }
}

function toggleRowExpand(
  loanId: string
) {
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

function formatPhone(
  phone?: string
) {
  return (
    phone?.trim() ||
    "—"
  );
}

function formatCurrency(
  amount: number
) {
  return new Intl.NumberFormat(
    props.isRTL
      ? "he-IL"
      : "en-US",

    {
      style:
        "currency",

      currency:
        "ILS",

      maximumFractionDigits:
        2,
    }
  ).format(
    Number(
      amount || 0
    )
  );
}

function getTypeLabelKey(
  type: LoanType
) {
  return (
    type ===
    LoanType.CHECKS
      ? "loanList.types.checks"
      : "loanList.types.standingOrders"
  );
}

function getStatusLabel(
  status: LoanStatus
) {
  if (
    props.isRTL
  ) {
    if (
      status ===
      "OVERDUE"
    ) {
      return "באיחור";
    }

    if (
      status ===
      "CLOSED"
    ) {
      return "סגורה";
    }

    return "פעילה";
  }

  if (
    status ===
    "OVERDUE"
  ) {
    return "Overdue";
  }

  if (
    status ===
    "CLOSED"
  ) {
    return "Closed";
  }

  return "Active";
}

function getStatusClass(
  status: LoanStatus
) {
  if (
    status ===
    "OVERDUE"
  ) {
    return (
      "bg-danger/10 " +
      "text-danger"
    );
  }

  if (
    status ===
    "CLOSED"
  ) {
    return (
      "bg-success/10 " +
      "text-success-deep"
    );
  }

  return (
    "bg-brand/10 " +
    "text-brand"
  );
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