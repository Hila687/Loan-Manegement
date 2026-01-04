<!-- frontend/client/src/components/loan-details/PaymentScheduleTab.vue -->
<template>
  <div>
    <!-- Loading -->
    <div v-if="loading" class="p-3 text-gray-500 italic">
      {{ t("payments.loading") }}
    </div>

    <!-- Error -->
    <div v-else-if="error" class="p-3 text-red-600">
      {{ t("payments.error") }}
    </div>

    <!-- Loaded but empty -->
    <div
      v-else-if="paymentsLoaded && payments.length === 0"
      class="p-3 text-gray-500 italic"
    >
      {{ t("payments.empty") }}
    </div>

    <!-- Loaded with data -->
    <div v-else-if="paymentsLoaded" class="space-y-4">
      <!-- Summary -->
      <div
        v-if="summary"
        class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3"
      >
        <div class="rounded-lg border bg-white p-3">
          <div class="text-xs text-gray-500">{{ t("payments.summary.totalAmount") }}</div>
          <div class="text-lg font-semibold">{{ formatCurrency(summary.total_amount) }}</div>
        </div>

        <div class="rounded-lg border bg-white p-3">
          <div class="text-xs text-gray-500">{{ t("payments.summary.paidAmount") }}</div>
          <div class="text-lg font-semibold">{{ formatCurrency(summary.paid_amount) }}</div>
        </div>

        <div class="rounded-lg border bg-white p-3">
          <div class="text-xs text-gray-500">{{ t("payments.summary.remainingAmount") }}</div>
          <div class="text-lg font-semibold">
            {{ formatCurrency(remainingAmount) }}
          </div>
        </div>

        <div class="rounded-lg border bg-white p-3">
          <div class="text-xs text-gray-500">{{ t("payments.summary.paymentsProgress") }}</div>
          <div class="text-lg font-semibold">
            {{ summary.paid_payments }} / {{ summary.total_payments }}
          </div>
        </div>
      </div>

      <!-- Table -->
      <div class="border rounded-lg overflow-hidden">
        <div class="max-h-80 overflow-y-auto">
          <table class="min-w-full divide-y divide-gray-200 text-sm">
            <thead class="bg-gray-50 sticky top-0">
              <tr>
                <th class="px-4 py-3 text-right font-semibold text-gray-700">
                  {{ t("payments.table.dueDate") }}
                </th>
                <th class="px-4 py-3 text-right font-semibold text-gray-700">
                  {{ t("payments.table.amountDue") }}
                </th>
                <th class="px-4 py-3 text-right font-semibold text-gray-700">
                  {{ t("payments.table.amountPaid") }}
                </th>
                <th class="px-4 py-3 text-right font-semibold text-gray-700">
                  {{ t("payments.table.status") }}
                </th>
              </tr>
            </thead>

            <tbody class="divide-y divide-gray-200 bg-white">
              <tr
                v-for="p in payments"
                :key="p.payment_id"
                class="hover:bg-gray-50"
              >
                <td class="px-4 py-3 text-gray-800">
                  {{ formatDate(p.due_date) }}
                </td>
                <td class="px-4 py-3 text-gray-800">
                  {{ formatCurrency(p.amount_due) }}
                </td>
                <td class="px-4 py-3 text-gray-800">
                  {{ formatCurrency(p.amount_paid) }}
                </td>
                <td class="px-4 py-3">
                  <span
                    class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
                    :class="statusPillClass(p.status)"
                  >
                    {{ statusLabel(p.status) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Not loaded yet -->
    <div v-else class="p-3 text-gray-500 italic">
      {{ t("payments.openToLoad") }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { getLoanPayments } from "../../services/paymentService";
import type { PaymentRow, PaymentSummary, PaymentStatus } from "../../types/payments";

const props = defineProps<{
  loanId: string;
  active: boolean;
}>();

const { t } = useI18n();

const loading = ref(false);
const error = ref(false);
const paymentsLoaded = ref(false);

const payments = ref<PaymentRow[]>([]);
const summary = ref<PaymentSummary | null>(null);

const remainingAmount = computed(() => {
  if (!summary.value) return 0;
  return Math.max(0, summary.value.total_amount - summary.value.paid_amount);
});

function formatCurrency(amount: number) {
  return new Intl.NumberFormat("he-IL", {
    style: "currency",
    currency: "ILS",
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatDate(dateStr: string) {
  const d = new Date(dateStr);
  return isNaN(d.getTime()) ? dateStr : d.toLocaleDateString("he-IL");
}

function statusLabel(status: PaymentStatus) {
  if (status === "PAID") return t("payments.status.paid");
  return t("payments.status.pending");
}

function statusPillClass(status: PaymentStatus) {
  return status === "PAID"
    ? "bg-green-50 text-green-700"
    : "bg-yellow-50 text-yellow-700";
}

async function fetchPaymentsOnce() {
  if (paymentsLoaded.value) return;

  loading.value = true;
  error.value = false;

  try {
    const data = await getLoanPayments(props.loanId);
    payments.value = Array.isArray(data?.payments) ? data.payments : [];
    summary.value = data?.summary ?? null;
    paymentsLoaded.value = true;
  } catch {
    error.value = true;
  } finally {
    loading.value = false;
  }
}

watch(
  () => props.active,
  (isActive) => {
    if (isActive) fetchPaymentsOnce();
  },
  { immediate: true }
);
</script>
