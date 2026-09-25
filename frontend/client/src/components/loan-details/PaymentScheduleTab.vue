<template>
  <div class="space-y-4">
    <div
      v-if="loading"
      class="flex items-center justify-center gap-3 rounded-xl border border-line bg-white p-6 text-sm text-muted"
    >
      <div
        class="h-5 w-5 animate-spin rounded-full border-2 border-brand border-t-transparent"
      ></div>
      {{ t("payments.loading") }}
    </div>

    <div
      v-else-if="error"
      class="rounded-xl border border-red-200 bg-red-50 p-4"
    >
      <div class="flex items-center justify-between gap-3">
        <p class="text-sm font-medium text-red-700">
          {{ t("payments.error") }}
        </p>

        <button
          type="button"
          class="rounded-lg bg-white px-4 py-2 text-sm font-semibold text-red-700 ring-1 ring-red-200 transition hover:bg-red-100"
          @click="loadPayments(true)"
        >
          {{ retryLabel }}
        </button>
      </div>
    </div>

    <div
      v-else-if="paymentsLoaded && payments.length === 0"
      class="rounded-xl border border-line bg-white p-6 text-center text-sm text-muted"
    >
      {{ t("payments.empty") }}
    </div>

    <div
      v-else-if="paymentsLoaded"
      class="space-y-4"
    >
      <div
        v-if="summary"
        class="grid grid-cols-2 gap-3 lg:grid-cols-4"
      >
        <div class="summary-card">
          <p class="summary-label">
            {{ t("payments.summary.totalAmount") }}
          </p>
          <p class="summary-value">
            {{ formatCurrency(summary.total_amount) }}
          </p>
        </div>

        <div class="summary-card">
          <p class="summary-label">
            {{ t("payments.summary.paidAmount") }}
          </p>
          <p class="summary-value">
            {{ formatCurrency(summary.paid_amount) }}
          </p>
        </div>

        <div class="summary-card">
          <p class="summary-label">
            {{ t("payments.summary.remainingAmount") }}
          </p>
          <p class="summary-value">
            {{ formatCurrency(remainingAmount) }}
          </p>
        </div>

        <div class="summary-card">
          <p class="summary-label">
            {{ t("payments.summary.paymentsProgress") }}
          </p>
          <p class="summary-value">
            <bdi
              dir="ltr"
              class="inline-block [unicode-bidi:isolate]"
            >
              {{ summary.paid_payments }} / {{ summary.total_payments }}
            </bdi>
          </p>
        </div>
      </div>

      <div class="flex justify-end">
        <button
          type="button"
          class="inline-flex items-center gap-2 rounded-lg border border-line bg-white px-3 py-2 text-xs font-semibold text-brand transition hover:border-brand hover:bg-brand/5"
          @click="loadPayments(true)"
        >
          <svg
            class="h-3.5 w-3.5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 4v6h6M20 20v-6h-6M5.5 16a7 7 0 0011.9 2M18.5 8a7 7 0 00-11.9-2"
            />
          </svg>
          {{ refreshLabel }}
        </button>
      </div>

      <!-- Desktop table -->
      <div class="hidden overflow-hidden rounded-xl border border-line sm:block">
        <div class="max-h-96 overflow-y-auto overflow-x-auto">
          <table class="min-w-full divide-y divide-line text-sm">
            <thead class="sticky top-0 z-10 bg-canvas">
              <tr>
                <th class="px-4 py-3 text-start font-semibold text-ink-soft">
                  {{ t("payments.table.dueDate") }}
                </th>
                <th class="px-4 py-3 text-start font-semibold text-ink-soft">
                  {{ t("payments.table.amountDue") }}
                </th>
                <th class="px-4 py-3 text-start font-semibold text-ink-soft">
                  {{ t("payments.table.amountPaid") }}
                </th>
                <th class="px-4 py-3 text-start font-semibold text-ink-soft">
                  {{ t("payments.table.status") }}
                </th>
                <th
                  v-if="auth.isAdmin.value"
                  class="px-4 py-3 text-start font-semibold text-ink-soft"
                >
                  {{ actionsLabel }}
                </th>
              </tr>
            </thead>

            <tbody class="divide-y divide-line bg-white">
              <template
                v-for="payment in payments"
                :key="payment.payment_id"
              >
                <tr class="hover:bg-canvas/70">
                  <td class="px-4 py-3 text-ink">
                    {{ formatDate(payment.due_date) }}
                  </td>
                  <td class="px-4 py-3 text-ink">
                    {{ formatCurrency(payment.amount_due) }}
                  </td>
                  <td class="px-4 py-3 text-ink">
                    {{ formatCurrency(payment.amount_paid) }}
                  </td>
                  <td class="px-4 py-3">
                    <div class="flex items-center gap-2">
                      <span
                        class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold"
                        :class="statusPillClass(payment.status)"
                      >
                        {{ statusLabel(payment.status) }}
                      </span>

                      <button
                        v-if="payment.exception_note"
                        type="button"
                        class="flex h-8 w-8 items-center justify-center rounded-full bg-warning/10 text-warning-deep transition hover:bg-warning/20"
                        :aria-label="noteLabel"
                        :title="noteLabel"
                        @click="toggleNote(payment.payment_id)"
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
                            d="M21 15a4 4 0 01-4 4H8l-5 3V7a4 4 0 014-4h10a4 4 0 014 4v8z"
                          />
                        </svg>
                      </button>
                    </div>
                  </td>
                  <td
                    v-if="auth.isAdmin.value"
                    class="px-4 py-3"
                  >
                    <button
                      type="button"
                      class="rounded-lg border border-brand/20 bg-brand/5 px-3 py-1.5 text-xs font-semibold text-brand transition hover:bg-brand/10"
                      @click="openPaymentEditor(payment)"
                    >
                      {{ editLabel }}
                    </button>
                  </td>
                </tr>

                <tr
                  v-if="openNotePaymentId === payment.payment_id && payment.exception_note"
                  class="bg-warning/5"
                >
                  <td
                    :colspan="auth.isAdmin.value ? 5 : 4"
                    class="px-4 py-3"
                  >
                    <div class="inline-flex max-w-xl items-start gap-2 rounded-xl border border-warning/20 bg-white px-3 py-2 text-sm text-ink-soft shadow-sm">
                      <svg
                        class="mt-0.5 h-4 w-4 flex-shrink-0 text-warning-deep"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M21 15a4 4 0 01-4 4H8l-5 3V7a4 4 0 014-4h10a4 4 0 014 4v8z"
                        />
                      </svg>
                      <span>{{ payment.exception_note }}</span>
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Mobile cards -->
      <div class="space-y-3 sm:hidden">
        <article
          v-for="payment in payments"
          :key="payment.payment_id"
          class="rounded-xl border border-line bg-white p-4"
        >
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="text-xs text-muted">
                {{ t("payments.table.dueDate") }}
              </p>
              <p class="mt-1 text-sm font-semibold text-ink">
                {{ formatDate(payment.due_date) }}
              </p>
            </div>

            <div class="flex items-center gap-2">
              <button
                v-if="payment.exception_note"
                type="button"
                class="flex h-8 w-8 items-center justify-center rounded-full bg-warning/10 text-warning-deep"
                :aria-label="noteLabel"
                @click="toggleNote(payment.payment_id)"
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
                    d="M21 15a4 4 0 01-4 4H8l-5 3V7a4 4 0 014-4h10a4 4 0 014 4v8z"
                  />
                </svg>
              </button>

              <span
                class="inline-flex rounded-full px-2.5 py-1 text-xs font-semibold"
                :class="statusPillClass(payment.status)"
              >
                {{ statusLabel(payment.status) }}
              </span>
            </div>
          </div>

          <div class="mt-4 grid grid-cols-2 gap-3">
            <div>
              <p class="text-xs text-muted">
                {{ t("payments.table.amountDue") }}
              </p>
              <p class="mt-1 text-sm font-medium text-ink">
                {{ formatCurrency(payment.amount_due) }}
              </p>
            </div>

            <div>
              <p class="text-xs text-muted">
                {{ t("payments.table.amountPaid") }}
              </p>
              <p class="mt-1 text-sm font-medium text-ink">
                {{ formatCurrency(payment.amount_paid) }}
              </p>
            </div>
          </div>

          <div
            v-if="openNotePaymentId === payment.payment_id && payment.exception_note"
            class="mt-3 rounded-xl border border-warning/20 bg-warning/5 px-3 py-2 text-sm text-ink-soft"
          >
            {{ payment.exception_note }}
          </div>

          <button
            v-if="auth.isAdmin.value"
            type="button"
            class="mt-3 w-full rounded-lg border border-brand/20 bg-brand/5 px-3 py-2 text-xs font-semibold text-brand"
            @click="openPaymentEditor(payment)"
          >
            {{ editLabel }}
          </button>
        </article>
      </div>
    </div>

    <div
      v-else
      class="rounded-xl border border-line bg-white p-4 text-sm italic text-muted"
    >
      {{ t("payments.openToLoad") }}
    </div>

    <Teleport to="body">
      <div
        v-if="auth.isAdmin.value && editingPayment"
        class="fixed inset-0 z-[120] flex items-center justify-center bg-black/45 p-4 backdrop-blur-sm"
        @click.self="closePaymentEditor"
      >
        <section
          class="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-2xl border border-line bg-white shadow-2xl"
          :dir="locale === 'he' ? 'rtl' : 'ltr'"
          role="dialog"
          aria-modal="true"
        >
          <header class="sticky top-0 z-10 flex items-start justify-between gap-4 border-b border-line bg-white px-5 py-4 sm:px-6">
            <div>
              <h3 class="text-lg font-bold text-ink">
                {{ editPaymentLabel }}
              </h3>
              <p class="mt-1 text-sm text-muted">
                {{ formatDate(editingPayment.due_date) }}
                ·
                {{ formatCurrency(editingPayment.amount_due) }}
              </p>
            </div>

            <button
              type="button"
              class="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full text-xl text-muted transition hover:bg-surface-muted hover:text-danger"
              :aria-label="closeLabel"
              @click="closePaymentEditor"
            >
              ×
            </button>
          </header>

          <div class="space-y-4 px-5 py-5 sm:px-6">
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <label class="flex flex-col gap-1.5">
                <span class="text-sm font-medium text-ink-soft">
                  {{ t("payments.table.status") }}
                </span>

                <select
                  v-model="exceptionStatus"
                  class="h-11 rounded-xl border border-line bg-white px-3 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/20"
                >
                  <option value="PENDING">
                    {{ t("payments.status.pending") }}
                  </option>
                  <option value="PAID">
                    {{ t("payments.status.paid") }}
                  </option>
                  <option value="LATE">
                    {{ lateLabel }}
                  </option>
                </select>
              </label>

              <label class="flex flex-col gap-1.5">
                <span class="text-sm font-medium text-ink-soft">
                  {{ amountPaidLabel }}
                </span>

                <input
                  v-model="exceptionAmountPaid"
                  type="number"
                  min="0"
                  step="0.01"
                  class="h-11 rounded-xl border border-line bg-white px-3 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/20"
                />
              </label>
            </div>

            <label class="flex flex-col gap-1.5">
              <span class="text-sm font-medium text-ink-soft">
                {{ noteLabel }}
              </span>

              <textarea
                v-model="exceptionNote"
                rows="3"
                maxlength="500"
                class="resize-none rounded-xl border border-line bg-white px-3 py-2.5 text-sm outline-none focus:border-brand focus:ring-2 focus:ring-brand/20"
                :placeholder="notePlaceholder"
              ></textarea>
            </label>

            <p
              v-if="exceptionError"
              class="rounded-lg bg-red-50 px-3 py-2 text-sm font-medium text-red-600"
            >
              {{ exceptionError }}
            </p>
          </div>

          <footer class="sticky bottom-0 flex flex-col-reverse gap-2 border-t border-line bg-white px-5 py-4 sm:flex-row sm:justify-end sm:px-6">
            <button
              v-if="editingPayment.is_manual_exception"
              type="button"
              :disabled="savingException"
              class="rounded-xl border border-line bg-white px-4 py-2.5 text-sm font-semibold text-ink-soft transition hover:bg-surface-muted disabled:opacity-50"
              @click="clearManualException"
            >
              {{ resetChangeLabel }}
            </button>

            <button
              type="button"
              :disabled="savingException"
              class="rounded-xl bg-brand px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-brand-deep disabled:opacity-50"
              @click="savePaymentEdit"
            >
              {{ savingException ? savingLabel : saveLabel }}
            </button>
          </footer>
        </section>
      </div>
    </Teleport>
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

const loading = ref(false);
const error = ref(false);
const paymentsLoaded = ref(false);
const payments = ref<PaymentRow[]>([]);
const summary = ref<PaymentSummary | null>(null);
const editingPayment = ref<PaymentRow | null>(null);
const openNotePaymentId = ref<string | null>(null);
const exceptionStatus = ref<PaymentStatus>("PENDING");
const exceptionAmountPaid = ref("0");
const exceptionNote = ref("");
const exceptionError = ref("");
const savingException = ref(false);


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


const remainingAmount =
  computed(() => {
    if (!summary.value) {
      return 0;
    }

    return Math.max(
      0,
      Number(summary.value.total_amount || 0) -
      Number(summary.value.paid_amount || 0)
    );
  });

const retryLabel = computed(() => text("נסה שוב", "Retry", "Intentar de nuevo"));
const refreshLabel = computed(() => text("רענון", "Refresh", "Actualizar"));
const actionsLabel = computed(() => text("פעולות", "Actions", "Acciones"));
const editLabel = computed(() => text("עריכה", "Edit", "Editar"));
const editPaymentLabel = computed(() => text("עריכת תשלום", "Edit payment", "Editar pago"));
const amountPaidLabel = computed(() => text("סכום ששולם", "Amount paid", "Importe pagado"));
const noteLabel = computed(() => text("הערה", "Note", "Nota"));
const notePlaceholder = computed(() => text("הערה...", "Note...", "Nota..."));
const resetChangeLabel = computed(() => text("איפוס שינוי", "Reset change", "Restablecer cambio"));
const saveLabel = computed(() => text("שמירה", "Save", "Guardar"));
const savingLabel = computed(() => text("שומר...", "Saving...", "Guardando..."));
const closeLabel = computed(() => text("סגירה", "Close", "Cerrar"));
const lateLabel = computed(() => text("באיחור", "Late", "Atrasado"));


function formatCurrency(
  amount: number | string
): string {
  const formatterLocale =
    locale.value === "he"
      ? "he-IL"
      : locale.value === "es"
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
    Number(amount || 0)
  );
}


function formatDate(
  dateStr: string
): string {
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

  const formatterLocale =
    locale.value === "he"
      ? "he-IL"
      : locale.value === "es"
        ? "es-ES"
        : "en-US";

  return date.toLocaleDateString(
    formatterLocale
  );
}


function statusLabel(
  status: PaymentStatus
): string {
  if (status === "PAID") {
    return t("payments.status.paid");
  }

  if (status === "LATE") {
    return lateLabel.value;
  }

  return t("payments.status.pending");
}


function statusPillClass(
  status: PaymentStatus
): string {
  if (status === "PAID") {
    return "bg-success/10 text-success-deep";
  }

  if (status === "LATE") {
    return "bg-danger/10 text-danger";
  }

  return "bg-warning/10 text-warning-deep";
}


function toggleNote(
  paymentId: string
): void {
  openNotePaymentId.value =
    openNotePaymentId.value === paymentId
      ? null
      : paymentId;
}


async function loadPayments(
  force = false
): Promise<void> {
  if (
    paymentsLoaded.value &&
    !force
  ) {
    return;
  }

  loading.value = true;
  error.value = false;

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
      data?.summary ?? null;

    paymentsLoaded.value =
      true;
  } catch {
    error.value = true;
  } finally {
    loading.value = false;
  }
}


function openPaymentEditor(
  payment: PaymentRow
): void {
  editingPayment.value =
    payment;

  exceptionStatus.value =
    payment.status;

  exceptionAmountPaid.value =
    String(
      payment.amount_paid || 0
    );

  exceptionNote.value =
    payment.exception_note || "";

  exceptionError.value = "";
}


function closePaymentEditor(): void {
  editingPayment.value = null;
  exceptionError.value = "";
}


async function savePaymentEdit(): Promise<void> {
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
      exceptionAmountPaid.value || 0
    );

  const amountDue =
    Number(
      editingPayment.value.amount_due || 0
    );

  if (!note) {
    exceptionError.value =
      text(
        "יש להזין הערה",
        "A note is required",
        "Se requiere una nota"
      );
    return;
  }

  if (
    !Number.isFinite(amountPaid) ||
    amountPaid < 0
  ) {
    exceptionError.value =
      text(
        "הסכום ששולם אינו תקין",
        "Invalid paid amount",
        "El importe pagado no es válido"
      );
    return;
  }

  if (amountPaid > amountDue) {
    exceptionError.value =
      text(
        "הסכום ששולם לא יכול להיות גדול מסכום התשלום",
        "Paid amount cannot exceed the scheduled amount",
        "El importe pagado no puede superar el importe programado"
      );
    return;
  }

  savingException.value = true;
  exceptionError.value = "";

  try {
    await updatePaymentException(
      editingPayment.value.payment_id,
      {
        status: exceptionStatus.value,
        amount_paid: amountPaid,
        note,
      }
    );

    closePaymentEditor();
    paymentsLoaded.value = false;
    await loadPayments(true);
  } catch (
    requestError: any
  ) {
    const data =
      requestError?.response?.data;

    exceptionError.value =
      data?.note?.[0] ||
      data?.amount_paid?.[0] ||
      data?.status?.[0] ||
      data?.detail ||
      text(
        "שמירת השינוי נכשלה",
        "Failed to save the payment change",
        "No se pudo guardar el cambio del pago"
      );
  } finally {
    savingException.value = false;
  }
}


async function clearManualException(): Promise<void> {
  if (
    !editingPayment.value ||
    savingException.value
  ) {
    return;
  }

  savingException.value = true;
  exceptionError.value = "";

  try {
    await updatePaymentException(
      editingPayment.value.payment_id,
      {
        clear_exception: true,
      }
    );

    closePaymentEditor();
    paymentsLoaded.value = false;
    await loadPayments(true);
  } catch (
    requestError: any
  ) {
    exceptionError.value =
      requestError?.response?.data?.detail ||
      text(
        "איפוס השינוי נכשל",
        "Failed to reset the change",
        "No se pudo restablecer el cambio"
      );
  } finally {
    savingException.value = false;
  }
}


watch(
  () => props.active,
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
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

.summary-card {
  border: 1px solid var(--color-line);
  border-radius: 0.75rem;
  background: white;
  padding: 0.75rem;
}

.summary-label {
  color: var(--color-muted);
  font-size: 0.75rem;
  line-height: 1rem;
}

.summary-value {
  margin-top: 0.25rem;
  color: var(--color-ink);
  font-size: 1rem;
  line-height: 1.5rem;
  font-weight: 600;
}

@media (min-width: 640px) {
  .summary-card {
    padding: 1rem;
  }

  .summary-value {
    font-size: 1.125rem;
    line-height: 1.75rem;
  }
}
</style>
