<template>
  <div class="space-y-4">
    <!-- Loading -->
    <div
      v-if="loading"
      class="flex items-center justify-center gap-3 rounded-xl border border-line bg-white p-6 text-sm text-muted"
    >
      <div
        class="h-5 w-5 animate-spin rounded-full border-2 border-brand border-t-transparent"
      ></div>

      {{ t("payments.loading") }}
    </div>

    <!-- Error -->
    <div
      v-else-if="error"
      class="rounded-xl border border-red-200 bg-red-50 p-4"
    >
      <div
        class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
      >
        <p
          class="text-sm font-medium text-red-700"
        >
          {{ t("payments.error") }}
        </p>

        <button
          type="button"
          class="self-start rounded-lg bg-white px-4 py-2 text-sm font-semibold text-red-700 ring-1 ring-red-200 transition hover:bg-red-100 sm:self-auto"
          @click="loadPayments(true)"
        >
          {{ retryLabel }}
        </button>
      </div>
    </div>

    <!-- Loaded but empty -->
    <div
      v-else-if="
        paymentsLoaded &&
        payments.length === 0
      "
      class="rounded-xl border border-line bg-white p-6 text-center text-sm text-muted"
    >
      {{ t("payments.empty") }}
    </div>

    <!-- Loaded with data -->
    <div
      v-else-if="paymentsLoaded"
      class="space-y-4"
    >
      <!-- Summary -->
      <div
        v-if="summary"
        class="grid grid-cols-2 gap-3 lg:grid-cols-4"
      >
        <div
          class="rounded-xl border border-line bg-white p-3 sm:p-4"
        >
          <div
            class="text-xs text-muted"
          >
            {{
              t(
                "payments.summary.totalAmount"
              )
            }}
          </div>

          <div
            class="mt-1 text-base font-semibold text-ink sm:text-lg"
          >
            {{
              formatCurrency(
                summary.total_amount
              )
            }}
          </div>
        </div>

        <div
          class="rounded-xl border border-line bg-white p-3 sm:p-4"
        >
          <div
            class="text-xs text-muted"
          >
            {{
              t(
                "payments.summary.paidAmount"
              )
            }}
          </div>

          <div
            class="mt-1 text-base font-semibold text-ink sm:text-lg"
          >
            {{
              formatCurrency(
                summary.paid_amount
              )
            }}
          </div>
        </div>

        <div
          class="rounded-xl border border-line bg-white p-3 sm:p-4"
        >
          <div
            class="text-xs text-muted"
          >
            {{
              t(
                "payments.summary.remainingAmount"
              )
            }}
          </div>

          <div
            class="mt-1 text-base font-semibold text-ink sm:text-lg"
          >
            {{
              formatCurrency(
                remainingAmount
              )
            }}
          </div>
        </div>

        <div
          class="rounded-xl border border-line bg-white p-3 sm:p-4"
        >
          <div
            class="text-xs text-muted"
          >
            {{
              t(
                "payments.summary.paymentsProgress"
              )
            }}
          </div>

          <div
            class="mt-1 text-base font-semibold text-ink sm:text-lg"
          >
            {{
              summary.paid_payments
            }}
            /
            {{
              summary.total_payments
            }}
          </div>
        </div>
      </div>

      <!-- Loan status -->
      <div
        class="flex flex-wrap items-center justify-between gap-3"
      >
        <span
          v-if="loanStatus"
          class="inline-flex rounded-full px-3 py-1 text-xs font-semibold"
          :class="loanStatusClass"
        >
          {{ loanStatusLabel }}
        </span>

        <button
          type="button"
          class="rounded-lg border border-line bg-white px-3 py-2 text-xs font-semibold text-brand transition hover:border-brand hover:bg-brand/5"
          @click="loadPayments(true)"
        >
          {{ refreshLabel }}
        </button>
      </div>

      <!-- Desktop table -->
      <div
        class="hidden overflow-hidden rounded-xl border border-line sm:block"
      >
        <div
          class="max-h-96 overflow-y-auto"
        >
          <table
            class="min-w-full divide-y divide-line text-sm"
          >
            <thead
              class="sticky top-0 bg-canvas"
            >
              <tr>
                <th
                  class="px-4 py-3 text-start font-semibold text-ink-soft"
                >
                  {{
                    t(
                      "payments.table.dueDate"
                    )
                  }}
                </th>

                <th
                  class="px-4 py-3 text-start font-semibold text-ink-soft"
                >
                  {{
                    t(
                      "payments.table.amountDue"
                    )
                  }}
                </th>

                <th
                  class="px-4 py-3 text-start font-semibold text-ink-soft"
                >
                  {{
                    t(
                      "payments.table.amountPaid"
                    )
                  }}
                </th>

                <th
                  class="px-4 py-3 text-start font-semibold text-ink-soft"
                >
                  {{
                    t(
                      "payments.table.status"
                    )
                  }}
                </th>

                <th
                  v-if="
                    auth.isAdmin.value
                  "
                  class="px-4 py-3 text-start font-semibold text-ink-soft"
                >
                  {{ actionsLabel }}
                </th>
              </tr>
            </thead>

            <tbody
              class="divide-y divide-line bg-white"
            >
              <tr
                v-for="
                  payment in payments
                "
                :key="
                  payment.payment_id
                "
                class="hover:bg-canvas/70"
              >
                <td
                  class="px-4 py-3 text-ink"
                >
                  {{
                    formatDate(
                      payment.due_date
                    )
                  }}
                </td>

                <td
                  class="px-4 py-3 text-ink"
                >
                  {{
                    formatCurrency(
                      payment.amount_due
                    )
                  }}
                </td>

                <td
                  class="px-4 py-3 text-ink"
                >
                  {{
                    formatCurrency(
                      payment.amount_paid
                    )
                  }}
                </td>

                <td
                  class="px-4 py-3"
                >
                  <div
                    class="flex flex-col items-start gap-1"
                  >
                    <span
                      class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold"
                      :class="
                        statusPillClass(
                          payment.status
                        )
                      "
                    >
                      {{
                        statusLabel(
                          payment.status
                        )
                      }}
                    </span>

                    <span
                      v-if="
                        payment.is_manual_exception
                      "
                      class="text-[11px] text-violet"
                    >
                      {{
                        manualExceptionLabel
                      }}
                    </span>
                  </div>
                </td>

                <td
                  v-if="
                    auth.isAdmin.value
                  "
                  class="px-4 py-3"
                >
                  <button
                    type="button"
                    class="rounded-lg border border-brand/20 bg-brand/5 px-3 py-1.5 text-xs font-semibold text-brand transition hover:bg-brand/10"
                    @click="
                      openExceptionEditor(
                        payment
                      )
                    "
                  >
                    {{
                      editExceptionLabel
                    }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Mobile cards -->
      <div
        class="space-y-3 sm:hidden"
      >
        <article
          v-for="
            payment in payments
          "
          :key="
            payment.payment_id
          "
          class="rounded-xl border border-line bg-white p-4"
        >
          <div
            class="flex items-start justify-between gap-3"
          >
            <div>
              <p
                class="text-xs text-muted"
              >
                {{
                  t(
                    "payments.table.dueDate"
                  )
                }}
              </p>

              <p
                class="mt-1 text-sm font-semibold text-ink"
              >
                {{
                  formatDate(
                    payment.due_date
                  )
                }}
              </p>
            </div>

            <span
              class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold"
              :class="
                statusPillClass(
                  payment.status
                )
              "
            >
              {{
                statusLabel(
                  payment.status
                )
              }}
            </span>
          </div>

          <div
            class="mt-4 grid grid-cols-2 gap-3"
          >
            <div>
              <p
                class="text-xs text-muted"
              >
                {{
                  t(
                    "payments.table.amountDue"
                  )
                }}
              </p>

              <p
                class="mt-1 text-sm font-medium text-ink"
              >
                {{
                  formatCurrency(
                    payment.amount_due
                  )
                }}
              </p>
            </div>

            <div>
              <p
                class="text-xs text-muted"
              >
                {{
                  t(
                    "payments.table.amountPaid"
                  )
                }}
              </p>

              <p
                class="mt-1 text-sm font-medium text-ink"
              >
                {{
                  formatCurrency(
                    payment.amount_paid
                  )
                }}
              </p>
            </div>
          </div>

          <div
            v-if="
              payment.is_manual_exception
            "
            class="mt-3 rounded-lg bg-violet/5 px-3 py-2 text-xs text-violet"
          >
            {{
              manualExceptionLabel
            }}

            <span
              v-if="
                payment.exception_note
              "
            >
              ·
              {{
                payment.exception_note
              }}
            </span>
          </div>

          <button
            v-if="
              auth.isAdmin.value
            "
            type="button"
            class="mt-3 w-full rounded-lg border border-brand/20 bg-brand/5 px-3 py-2 text-xs font-semibold text-brand"
            @click="
              openExceptionEditor(
                payment
              )
            "
          >
            {{
              editExceptionLabel
            }}
          </button>
        </article>
      </div>
    </div>

    <!-- Not loaded yet -->
    <div
      v-else
      class="rounded-xl border border-line bg-white p-4 text-sm italic text-muted"
    >
      {{
        t(
          "payments.openToLoad"
        )
      }}
    </div>

    <!-- Admin exception editor -->
    <div
      v-if="
        auth.isAdmin.value &&
        editingPayment
      "
      class="rounded-xl border border-brand/20 bg-brand-soft p-4 sm:p-5"
    >
      <div
        class="flex items-start justify-between gap-4"
      >
        <div>
          <h3
            class="font-semibold text-ink"
          >
            {{ exceptionTitle }}
          </h3>

          <p
            class="mt-1 text-xs text-muted"
          >
            {{
              formatDate(
                editingPayment.due_date
              )
            }}
            ·
            {{
              formatCurrency(
                editingPayment.amount_due
              )
            }}
          </p>
        </div>

        <button
          type="button"
          class="text-xl text-muted transition hover:text-danger"
          @click="
            closeExceptionEditor
          "
        >
          ×
        </button>
      </div>

      <div
        class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2"
      >
        <label
          class="flex flex-col gap-1.5"
        >
          <span
            class="text-sm font-medium text-ink-soft"
          >
            {{
              t(
                "payments.table.status"
              )
            }}
          </span>

          <select
            v-model="
              exceptionStatus
            "
            class="h-11 rounded-lg border border-line bg-white px-3 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/20"
          >
            <option
              value="PENDING"
            >
              {{
                statusLabel(
                  "PENDING"
                )
              }}
            </option>

            <option
              value="PAID"
            >
              {{
                statusLabel(
                  "PAID"
                )
              }}
            </option>

            <option
              value="LATE"
            >
              {{
                statusLabel(
                  "LATE"
                )
              }}
            </option>
          </select>
        </label>

        <label
          class="flex flex-col gap-1.5"
        >
          <span
            class="text-sm font-medium text-ink-soft"
          >
            {{ amountPaidLabel }}
          </span>

          <input
            v-model="
              exceptionAmountPaid
            "
            type="number"
            inputmode="decimal"
            min="0"
            step="0.01"
            class="h-11 rounded-lg border border-line bg-white px-3 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/20"
          />
        </label>
      </div>

      <label
        class="mt-4 flex flex-col gap-1.5"
      >
        <span
          class="text-sm font-medium text-ink-soft"
        >
          {{ exceptionNoteLabel }}
        </span>

        <textarea
          v-model="
            exceptionNote
          "
          rows="3"
          maxlength="500"
          class="rounded-lg border border-line bg-white px-3 py-2 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/20"
        ></textarea>
      </label>

      <p
        v-if="
          exceptionError
        "
        class="mt-3 text-sm text-red-600"
      >
        {{ exceptionError }}
      </p>

      <div
        class="mt-4 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end"
      >
        <button
          v-if="
            editingPayment.is_manual_exception
          "
          type="button"
          :disabled="
            savingException
          "
          class="rounded-lg border border-line bg-white px-4 py-2 text-sm font-semibold text-ink-soft transition hover:bg-surface-muted disabled:opacity-50"
          @click="
            clearManualException
          "
        >
          {{
            clearExceptionLabel
          }}
        </button>

        <button
          type="button"
          :disabled="
            savingException
          "
          class="rounded-lg bg-brand px-4 py-2 text-sm font-semibold text-white transition hover:bg-brand-deep disabled:opacity-50"
          @click="
            saveManualException
          "
        >
          {{
            savingException
              ? savingLabel
              : saveLabel
          }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import {
  computed,
  ref,
  watch,
} from "vue";

import {
  useI18n,
} from "vue-i18n";

import {
  useAuth,
} from "../../composables/useAuth";

import {
  getLoanPayments,
  updatePaymentException,
} from "../../services/paymentService";

import type {
  PaymentRow,
  PaymentStatus,
  PaymentSummary,
} from "../../types/payments";

const props =
  defineProps<{
    loanId: string;
    active: boolean;
  }>();

const {
  t,
  locale,
} = useI18n();

const auth =
  useAuth();

const loading =
  ref(false);

const error =
  ref(false);

const paymentsLoaded =
  ref(false);

const payments =
  ref<PaymentRow[]>([]);

const summary =
  ref<PaymentSummary | null>(
    null
  );

const loanStatus =
  ref<
    | "ACTIVE"
    | "OVERDUE"
    | "CLOSED"
    | ""
  >("");

const editingPayment =
  ref<PaymentRow | null>(
    null
  );

const exceptionStatus =
  ref<PaymentStatus>(
    "PENDING"
  );

const exceptionAmountPaid =
  ref("0");

const exceptionNote =
  ref("");

const exceptionError =
  ref("");

const savingException =
  ref(false);

const isHebrew =
  computed(
    () =>
      locale.value ===
      "he"
  );

const remainingAmount =
  computed(() => {
    if (!summary.value) {
      return 0;
    }

    return Math.max(
      0,
      Number(
        summary.value
          .total_amount ||
          0
      ) -
        Number(
          summary.value
            .paid_amount ||
            0
        )
    );
  });

const retryLabel =
  computed(() =>
    isHebrew.value
      ? "נסה שוב"
      : "Retry"
  );

const refreshLabel =
  computed(() =>
    isHebrew.value
      ? "רענון"
      : "Refresh"
  );

const actionsLabel =
  computed(() =>
    isHebrew.value
      ? "פעולות"
      : "Actions"
  );

const manualExceptionLabel =
  computed(() =>
    isHebrew.value
      ? "חריגה ידנית"
      : "Manual exception"
  );

const editExceptionLabel =
  computed(() =>
    isHebrew.value
      ? "עריכת חריגה"
      : "Edit exception"
  );

const exceptionTitle =
  computed(() =>
    isHebrew.value
      ? "חריגה בתשלום"
      : "Payment exception"
  );

const amountPaidLabel =
  computed(() =>
    isHebrew.value
      ? "סכום ששולם"
      : "Amount paid"
  );

const exceptionNoteLabel =
  computed(() =>
    isHebrew.value
      ? "סיבת החריגה"
      : "Exception note"
  );

const clearExceptionLabel =
  computed(() =>
    isHebrew.value
      ? "חזרה לחישוב אוטומטי"
      : "Return to automatic status"
  );

const saveLabel =
  computed(() =>
    isHebrew.value
      ? "שמירה"
      : "Save"
  );

const savingLabel =
  computed(() =>
    isHebrew.value
      ? "שומר..."
      : "Saving..."
  );

const loanStatusLabel =
  computed(() => {
    if (
      loanStatus.value ===
      "OVERDUE"
    ) {
      return isHebrew.value
        ? "הלוואה באיחור"
        : "Loan overdue";
    }

    if (
      loanStatus.value ===
      "CLOSED"
    ) {
      return isHebrew.value
        ? "הלוואה סגורה"
        : "Loan closed";
    }

    return isHebrew.value
      ? "הלוואה פעילה"
      : "Loan active";
  });

const loanStatusClass =
  computed(() => {
    if (
      loanStatus.value ===
      "OVERDUE"
    ) {
      return (
        "bg-danger/10 " +
        "text-danger"
      );
    }

    if (
      loanStatus.value ===
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
  });

function formatCurrency(
  amount:
    | number
    | string
) {
  return new Intl.NumberFormat(
    isHebrew.value
      ? "he-IL"
      : "en-US",
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
  dateStr: string
) {
  const date =
    new Date(
      `${dateStr}T00:00:00`
    );

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return dateStr;
  }

  return date.toLocaleDateString(
    isHebrew.value
      ? "he-IL"
      : "en-US"
  );
}

function statusLabel(
  status: PaymentStatus
) {
  if (
    status === "PAID"
  ) {
    return t(
      "payments.status.paid"
    );
  }

  if (
    status === "LATE"
  ) {
    return isHebrew.value
      ? "באיחור"
      : "Late";
  }

  return t(
    "payments.status.pending"
  );
}

function statusPillClass(
  status: PaymentStatus
) {
  if (
    status === "PAID"
  ) {
    return (
      "bg-success/10 " +
      "text-success-deep"
    );
  }

  if (
    status === "LATE"
  ) {
    return (
      "bg-danger/10 " +
      "text-danger"
    );
  }

  return (
    "bg-warning/10 " +
    "text-warning-deep"
  );
}

async function loadPayments(
  force = false
) {
  if (
    paymentsLoaded.value &&
    !force
  ) {
    return;
  }

  loading.value =
    true;

  error.value =
    false;

  try {
    const data =
      await getLoanPayments(
        props.loanId
      );

    payments.value =
      Array.isArray(
        data?.payments
      )
        ? data.payments
        : [];

    summary.value =
      data?.summary ??
      null;

    loanStatus.value =
      data?.loan_status ||
      "";

    paymentsLoaded.value =
      true;
  } catch {
    error.value =
      true;
  } finally {
    loading.value =
      false;
  }
}

function openExceptionEditor(
  payment: PaymentRow
) {
  editingPayment.value =
    payment;

  exceptionStatus.value =
    payment.status;

  exceptionAmountPaid.value =
    String(
      payment.amount_paid ||
      0
    );

  exceptionNote.value =
    payment.exception_note ||
    "";

  exceptionError.value =
    "";
}

function closeExceptionEditor() {
  editingPayment.value =
    null;

  exceptionError.value =
    "";
}

async function saveManualException() {
  if (
    !editingPayment.value ||
    savingException.value
  ) {
    return;
  }

  const note =
    exceptionNote.value.trim();

  const amountPaid =
    Number(
      exceptionAmountPaid.value ||
      0
    );

  const amountDue =
    Number(
      editingPayment.value
        .amount_due ||
      0
    );

  if (!note) {
    exceptionError.value =
      isHebrew.value
        ? "יש להזין סיבה לחריגה"
        : "An exception note is required";

    return;
  }

  if (
    !Number.isFinite(
      amountPaid
    ) ||
    amountPaid < 0
  ) {
    exceptionError.value =
      isHebrew.value
        ? "הסכום ששולם אינו תקין"
        : "Invalid paid amount";

    return;
  }

  if (
    amountPaid >
    amountDue
  ) {
    exceptionError.value =
      isHebrew.value
        ? "הסכום ששולם לא יכול להיות גדול מסכום התשלום"
        : "Paid amount cannot exceed the scheduled amount";

    return;
  }

  savingException.value =
    true;

  exceptionError.value =
    "";

  try {
    await updatePaymentException(
      editingPayment.value
        .payment_id,
      {
        status:
          exceptionStatus.value,

        amount_paid:
          amountPaid,

        note,
      }
    );

    closeExceptionEditor();

    paymentsLoaded.value =
      false;

    await loadPayments(
      true
    );
  } catch (
    requestError: any
  ) {
    const data =
      requestError
        ?.response
        ?.data;

    exceptionError.value =
      data?.note?.[0] ||
      data?.amount_paid?.[0] ||
      data?.status?.[0] ||
      data?.detail ||
      (
        isHebrew.value
          ? "שמירת החריגה נכשלה"
          : "Failed to save exception"
      );
  } finally {
    savingException.value =
      false;
  }
}

async function clearManualException() {
  if (
    !editingPayment.value ||
    savingException.value
  ) {
    return;
  }

  savingException.value =
    true;

  exceptionError.value =
    "";

  try {
    await updatePaymentException(
      editingPayment.value
        .payment_id,
      {
        clear_exception:
          true,
      }
    );

    closeExceptionEditor();

    paymentsLoaded.value =
      false;

    await loadPayments(
      true
    );
  } catch (
    requestError: any
  ) {
    exceptionError.value =
      requestError
        ?.response
        ?.data
        ?.detail ||
      (
        isHebrew.value
          ? "ביטול החריגה נכשל"
          : "Failed to clear exception"
      );
  } finally {
    savingException.value =
      false;
  }
}

watch(
  () =>
    props.active,

  (isActive) => {
    if (isActive) {
      loadPayments();
    }
  },

  {
    immediate: true,
  }
);
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