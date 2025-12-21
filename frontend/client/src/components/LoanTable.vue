<template>
  <div class="bg-white rounded-xl border border-[#E5E5EA] overflow-hidden shadow-sm">
    <!-- Desktop Table -->
    <div class="hidden md:block overflow-x-auto">
      <table class="min-w-full divide-y divide-[#E5E5EA]">
        <thead class="bg-[#F7F8FC]">
          <tr>
            <th class="px-4 py-3 w-8"></th>

            <th
              v-for="column in columns"
              :key="column.key"
              class="px-4 py-3 text-sm font-semibold"
              :class="isRTL ? 'text-right' : 'text-left'"
              :style="column.minWidth ? `min-width:${column.minWidth}` : ''"
            >
              {{ t(column.labelKey) }}
            </th>
          </tr>
        </thead>

        <tbody class="divide-y divide-[#E5E5EA]">
          <template v-for="loan in loans" :key="loan.id">
            <tr class="hover:bg-[#F7F8FC]/50">
              <!-- Expand -->
              <td class="px-4 py-4 text-center">
                <button @click.stop="toggleRowExpand(loan.id)">
                  <svg
                    class="w-4 h-4 transition-transform"
                    :class="expandedLoanId === loan.id ? 'rotate-180' : ''"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </td>

              <!-- Borrower Name -->
              <td class="px-4 py-4">
                <div class="text-sm font-medium text-[#111827]">
                  {{ loan.borrower.name || "—" }}
                </div>
              </td>

              <!-- Phone -->
              <td class="px-4 py-4">
                <div class="text-sm text-[#111827]">
                  {{ formatPhone(loan.borrower.phone) }}
                </div>
              </td>

              <!-- Email -->
              <td class="px-4 py-4 text-sm text-[#111827]">
                {{ loan.borrower.email || "—" }}
              </td>

              <!-- Trustee -->
              <td class="px-4 py-4 text-sm text-[#111827]">
                {{ loan.trustee?.name || "—" }}
              </td>

              <!-- Amount -->
              <td class="px-4 py-4">
                <span class="text-sm text-[#111827]">
                  {{ formatCurrency(loan.amount) }}
                </span>
              </td>

              <!-- Type -->
              <td class="px-4 py-4">
                <span
                  class="px-3 py-1 rounded-full text-xs font-medium"
                  :class="loan.type === 'checks'
                    ? 'bg-[#007AFF]/10 text-[#007AFF]'
                    : 'bg-[#FF9500]/10 text-[#FF9500]'"
                >
                  {{ t(getTypeLabelKey(loan.type)) }}
                </span>
              </td>
            </tr>

            <!-- Expanded Details -->
            <tr v-if="expandedLoanId === loan.id">
              <td :colspan="columns.length + 1" class="px-4 py-6 bg-[#F7F8FC]/30">
                <!-- Loading -->
                <div v-if="loadingDetails[loan.id]" class="flex justify-center py-8">
                  <div class="h-8 w-8 animate-spin rounded-full border-4 border-[#007AFF] border-t-transparent"></div>
                </div>

                <!-- Error -->
                <div
                  v-else-if="detailsError[loan.id]"
                  class="text-center py-6 text-red-600"
                >
                  <p>שגיאה בטעינת פרטי ההלוואה</p>
                  <button 
                    @click="loadLoanDetails(loan.id)"
                    class="mt-2 px-4 py-2 bg-[#007AFF] text-white rounded-lg hover:bg-[#0051D5]"
                  >
                    נסה שוב
                  </button>
                </div>

                <!-- Details Panel -->
                <LoanDetailsPanel
                  v-else-if="loanDetails[loan.id]"
                  :loan="loanDetails[loan.id]"
                />
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <!-- Mobile -->
    <div class="md:hidden divide-y">
      <div v-for="loan in loans" :key="loan.id" class="p-4">
        <button class="w-full text-right" @click="toggleRowExpand(loan.id)">
          <div class="flex justify-between items-center">
            <div>
              <div class="font-semibold">{{ loan.borrower.name || "—" }}</div>
              <div class="text-xs text-gray-500">
                {{ formatPhone(loan.borrower.phone) }}
              </div>
            </div>

            <div class="text-gray-700">
              {{ formatCurrency(loan.amount) }}
            </div>
          </div>
        </button>

        <div class="mt-2 text-sm">
          <div>📧 {{ loan.borrower.email || "—" }}</div>
          <div>👤 {{ loan.trustee?.name || "—" }}</div>
          <div class="mt-1">
            <span
              class="px-2 py-1 rounded-full text-xs"
              :class="loan.type === 'checks'
                ? 'bg-blue-100 text-blue-600'
                : 'bg-orange-100 text-orange-600'"
            >
              {{ t(getTypeLabelKey(loan.type)) }}
            </span>
          </div>
        </div>

        <div v-if="expandedLoanId === loan.id" class="mt-4">
          <!-- Loading -->
          <div v-if="loadingDetails[loan.id]" class="flex justify-center py-4">
            <div class="h-6 w-6 animate-spin rounded-full border-4 border-[#007AFF] border-t-transparent"></div>
          </div>

          <!-- Error -->
          <div v-else-if="detailsError[loan.id]" class="text-center py-4 text-red-600 text-sm">
            <p>שגיאה בטעינת הפרטים</p>
            <button 
              @click="loadLoanDetails(loan.id)"
              class="mt-2 px-3 py-1 bg-[#007AFF] text-white rounded-lg text-xs"
            >
              נסה שוב
            </button>
          </div>

          <!-- Details -->
          <LoanDetailsPanel
            v-else-if="loanDetails[loan.id]"
            :loan="loanDetails[loan.id]"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from "vue";
import type { LoanListItem, Loan } from "../types/loan";
import { LoanType } from "../types/loan";
import LoanDetailsPanel from "./loan-details/LoanDetailsPanel.vue";
import loanService from "../services/loanService";

interface Props {
  loans: LoanListItem[];
  isRTL: boolean;
  t: (key: string) => string;
  openedLoanId?: string | null;
}

const props = withDefaults(defineProps<Props>(), {
  openedLoanId: null,
});

const emit = defineEmits<{
  (e: "toggle-loan", loanId: string | null): void;
}>();

const expandedLoanId = computed(() => props.openedLoanId);
const loanDetails = reactive<Record<string, Loan>>({});
const loadingDetails = reactive<Record<string, boolean>>({});
const detailsError = reactive<Record<string, boolean>>({});

const columns = [
  { key: "borrower", labelKey: "loanList.table.borrower", minWidth: "180px" },
  { key: "phone", labelKey: "loanList.table.phone", minWidth: "140px" },
  { key: "email", labelKey: "loanList.table.email", minWidth: "200px" },
  { key: "trustee", labelKey: "loanList.table.trustee", minWidth: "180px" },
  { key: "amount", labelKey: "loanList.table.amount", minWidth: "120px" },
  { key: "type", labelKey: "loanList.table.type", minWidth: "140px" },
];

const loadLoanDetails = async (loanId: string) => {
  if (loanDetails[loanId]) return;

  loadingDetails[loanId] = true;
  detailsError[loanId] = false;

  try {
    const details = await loanService.getLoanDetails(loanId);
    loanDetails[loanId] = details;

    if (import.meta.env.DEV) {
      console.log("Loaded loan details:", details);
    }
  } catch (error) {
    console.error("Failed to load loan details:", error);
    detailsError[loanId] = true;
  } finally {
    loadingDetails[loanId] = false;
  }
};

const toggleRowExpand = async (loanId: string) => {
  const next = expandedLoanId.value === loanId ? null : loanId;
  emit("toggle-loan", next);
};

// Watch for opened loan ID and load details
watch(
  () => props.openedLoanId,
  (loanId) => {
    if (loanId) {
      loadLoanDetails(loanId);
    }
  },
  { immediate: true }
);

const formatPhone = (phone?: string) =>
  phone ? phone.replace(/(\d{3})(\d{3})(\d{4})/, "$1-$2-$3") : "—";

const formatCurrency = (amount: number) =>
  new Intl.NumberFormat("he-IL", {
    style: "currency",
    currency: "ILS",
    maximumFractionDigits: 0,
  }).format(amount);

const getTypeLabelKey = (type: LoanType) =>
  type === LoanType.CHECKS
    ? "loanList.types.checks"
    : "loanList.types.standingOrders";
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