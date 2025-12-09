<template>
  <div class="bg-white rounded-xl border border-[#E5E5EA] overflow-hidden shadow-sm">
    <!-- Table container with scroll -->
    <div class="overflow-x-auto">
      <div class="inline-block min-w-full align-middle">
        <div class="overflow-hidden">
          <table class="min-w-full divide-y divide-[#E5E5EA]">
            <!-- Table header -->
            <thead class="bg-[#F7F8FC]">
              <tr>
                <th
                  v-for="column in columns"
                  :key="column.key"
                  scope="col"
                  :class="[
                    'px-4 py-3.5 text-sm font-semibold',
                    isRTL ? 'text-right' : 'text-left',
                  ]"
                  :style="column.minWidth ? `min-width: ${column.minWidth}` : ''"
                >
                  <div class="flex items-center gap-2">
                    <svg
                      v-if="column.icon === 'user'"
                      class="w-4 h-4 text-[#6B7280]"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                      />
                    </svg>
                    <svg
                      v-else-if="column.icon === 'email'"
                      class="w-4 h-4 text-[#6B7280]"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                      />
                    </svg>
                    <svg
                      v-else-if="column.icon === 'trustee'"
                      class="w-4 h-4 text-[#6B7280]"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                      />
                    </svg>
                    <svg
                      v-else-if="column.icon === 'amount'"
                      class="w-4 h-4 text-[#6B7280]"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"
                      />
                    </svg>
                    <svg
                      v-else-if="column.icon === 'type'"
                      class="w-4 h-4 text-[#6B7280]"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
                      />
                    </svg>
                    <span class="text-[#111827]">{{ t(column.labelKey) }}</span>
                  </div>
                </th>
              </tr>
            </thead>

            <!-- Table body -->
            <tbody class="divide-y divide-[#E5E5EA] bg-white">
              <tr
                v-for="loan in loans"
                :key="loan.id"
                class="transition-colors hover:bg-[#F7F8FC]/50 cursor-pointer group"
                @click="handleRowClick(loan)"
              >
                <!-- Borrower Name -->
                <td class="whitespace-nowrap px-4 py-4">
                  <div class="flex items-center gap-3">
                    <div
                      class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-[#007AFF]/10 transition-colors group-hover:bg-[#007AFF]/20"
                    >
                      <svg
                        class="w-5 h-5 text-[#007AFF]"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                        />
                      </svg>
                    </div>
                    <div class="min-w-0 flex-1">
                      <p
                        class="text-sm font-medium text-[#111827] truncate"
                        :dir="isRTL ? 'rtl' : 'ltr'"
                      >
                        {{ loan.borrower_name }}
                      </p>
                      <p
                        class="text-xs text-[#6B7280] truncate"
                        :dir="isRTL ? 'rtl' : 'ltr'"
                      >
                        {{ formatPhone(loan.borrower_phone) }}
                      </p>
                    </div>
                  </div>
                </td>

                <!-- Email -->
                <td class="whitespace-nowrap px-4 py-4">
                  <div v-if="loan.borrower_email" class="flex items-center gap-2">
                    <svg
                      class="w-4 h-4 text-[#6B7280] flex-shrink-0"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                      />
                    </svg>
                    <p
                      class="text-sm text-[#111827] truncate"
                      :dir="isRTL ? 'rtl' : 'ltr'"
                    >
                      {{ loan.borrower_email }}
                    </p>
                  </div>
                  <span v-else class="text-sm text-[#6B7280]">—</span>
                </td>

                <!-- Trustee -->
                <td class="whitespace-nowrap px-4 py-4">
                  <div class="min-w-0">
                    <div class="flex items-center gap-2 mb-1">
                      <svg
                        class="w-4 h-4 text-[#FF9500] flex-shrink-0"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                        />
                      </svg>
                      <p
                        class="text-sm font-medium text-[#111827] truncate"
                        :dir="isRTL ? 'rtl' : 'ltr'"
                      >
                        {{ loan.trustee_name }}
                      </p>
                    </div>
                    <p
                      v-if="loan.trustee_community"
                      class="text-xs text-[#6B7280] truncate"
                      :dir="isRTL ? 'rtl' : 'ltr'"
                    >
                      {{ loan.trustee_community }}
                    </p>
                  </div>
                </td>

                <!-- Amount -->
                <td class="whitespace-nowrap px-4 py-4">
                  <div
                    class="inline-flex items-center gap-1.5 rounded-full bg-[#34C759]/10 px-3 py-1.5 transition-colors group-hover:bg-[#34C759]/20"
                  >
                    <svg
                      class="w-3.5 h-3.5 text-[#34C759]"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"
                      />
                    </svg>
                    <span class="text-sm font-semibold text-[#34C759]">
                      {{ formatCurrency(loan.amount) }}
                    </span>
                  </div>
                </td>

                <!-- Type Badge -->
                <td class="whitespace-nowrap px-4 py-4">
                  <span
                    :class="[
                      'inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium transition-colors',
                      loan.type === 'checks'
                        ? 'bg-[#007AFF]/10 text-[#007AFF] group-hover:bg-[#007AFF]/20'
                        : 'bg-[#FF9500]/10 text-[#FF9500] group-hover:bg-[#FF9500]/20',
                    ]"
                  >
                    <svg
                      class="w-3.5 h-3.5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        v-if="loan.type === 'checks'"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                      />
                      <path
                        v-else
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                      />
                    </svg>
                    {{ t(getTypeLabelKey(loan.type)) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div
      v-if="loans.length === 0 && !loading"
      class="flex flex-col items-center justify-center py-16 px-4"
    >
      <div
        class="flex h-20 w-20 items-center justify-center rounded-full bg-[#6B7280]/10 mb-4"
      >
        <svg
          class="w-10 h-10 text-[#6B7280]"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
      </div>
      <p class="text-lg font-semibold text-[#111827] mb-2">
        {{ t(emptyMessage) }}
      </p>
      <p class="text-sm text-[#6B7280] text-center max-w-md">
        {{ t(emptyDescription) }}
      </p>
    </div>

    <!-- Loading state -->
    <div
      v-if="loading"
      class="flex flex-col items-center justify-center py-16"
    >
      <div
        class="h-12 w-12 animate-spin rounded-full border-4 border-[#007AFF] border-t-transparent mb-4"
      ></div>
      <p class="text-sm font-medium text-[#6B7280]">
        {{ t("loanList.messages.loading") }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import type { LoanListItem, LoanType } from "../types/loan";

interface Column {
  key: string;
  labelKey: string;
  minWidth?: string;
  icon?: string;
}

interface Props {
  loans: LoanListItem[];
  loading?: boolean;
  isRTL: boolean;
  t: (key: string) => string;
  emptyMessage?: string;
  emptyDescription?: string;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  emptyMessage: "loanList.messages.noLoans",
  emptyDescription: "loanList.messages.noLoansDesc",
});

const emit = defineEmits<{
  rowClick: [loan: LoanListItem];
}>();

// Table columns configuration
const columns = computed<Column[]>(() => [
  { key: "borrower", labelKey: "loanList.table.borrower", minWidth: "200px", icon: "user" },
  { key: "email", labelKey: "loanList.table.email", minWidth: "200px", icon: "email" },
  { key: "trustee", labelKey: "loanList.table.trustee", minWidth: "180px", icon: "trustee" },
  { key: "amount", labelKey: "loanList.table.amount", minWidth: "140px", icon: "amount" },
  { key: "type", labelKey: "loanList.table.type", minWidth: "140px", icon: "type" },
]);

// Format phone number for display
const formatPhone = (phone: string): string => {
  if (!phone) return "—";
  const cleaned = phone.replace(/\D/g, "");
  if (cleaned.length === 10) {
    return cleaned.replace(/(\d{3})(\d{3})(\d{4})/, "$1-$2-$3");
  }
  return phone;
};

// Format currency
const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat("he-IL", {
    style: "currency",
    currency: "ILS",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

// Map backend type to i18n label key
const getTypeLabelKey = (type: LoanType): string => {
  return type === "checks"
    ? "loanList.types.checks"
    : "loanList.types.standingOrders";
};

// Handle row click
const handleRowClick = (loan: LoanListItem) => {
  emit("rowClick", loan);
};
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

tbody tr {
  transition: background-color 0.15s ease;
}

.overflow-x-auto::-webkit-scrollbar {
  height: 8px;
}

.overflow-x-auto::-webkit-scrollbar-track {
  background: #f7f8fc;
  border-radius: 4px;
}

.overflow-x-auto::-webkit-scrollbar-thumb {
  background: #e5e5ea;
  border-radius: 4px;
}

.overflow-x-auto::-webkit-scrollbar-thumb:hover {
  background: #d1d1d6;
}
</style>
