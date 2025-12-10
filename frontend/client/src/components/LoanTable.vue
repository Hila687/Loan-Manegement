<template>
  <div class="bg-white rounded-xl border border-[#E5E5EA] overflow-hidden shadow-sm">
    <!-- Desktop Table (md and above) -->
    <div class="hidden md:block overflow-x-auto">
      <div class="inline-block min-w-full align-middle">
        <div class="overflow-hidden">
          <table class="min-w-full divide-y divide-[#E5E5EA]">
            <!-- Table header -->
            <thead class="bg-[#F7F8FC]">
              <tr>
                <th scope="col" class="px-4 py-3.5 w-8"></th>
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
                        d="M7 7h.01M7 3h5a2 2 0 011.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A2 2 0 013 12V7a4 4 0 014-4z"
                      />
                    </svg>
                    <span class="text-[#111827]">{{ t(column.labelKey) }}</span>
                  </div>
                </th>
              </tr>
            </thead>

            <!-- Table body -->
            <tbody class="divide-y divide-[#E5E5EA] bg-white">
              <template v-for="(loan, index) in loans" :key="loan.id ?? index">
                <tr class="transition-colors hover:bg-[#F7F8FC]/50 group cursor-pointer">
                  <!-- Expand Icon -->
                  <td class="px-4 py-4 text-center">
                    <button
                      type="button"
                      class="inline-flex items-center justify-center rounded-full p-1 hover:bg-[#E5E7EB] focus:outline-none"
                      @click.stop="toggleRowExpand(index)"
                    >
                      <svg
                        :class="[
                          'w-4 h-4 text-[#6B7280] transition-transform',
                          expandedRowIndex === index ? 'rotate-180' : ''
                        ]"
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
                          {{ loan.borrower.name }}
                        </p>
                        <p
                          class="text-xs text-[#6B7280] truncate"
                          :dir="isRTL ? 'rtl' : 'ltr'"
                        >
                          {{ formatPhone(loan.borrower.phone) }}
                        </p>
                      </div>
                    </div>
                  </td>

                  <!-- Email -->
                  <td class="whitespace-nowrap px-4 py-4">
                    <div v-if="loan.borrower.email" class="flex items-center gap-2">
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
                        {{ loan.borrower.email }}
                      </p>
                    </div>
                    <span v-else class="text-sm text-[#6B7280]">—</span>
                  </td>

                  <!-- Amount -->
                  <td class="whitespace-nowrap px-4 py-4">
                    <div
                      class="inline-flex items-center gap-1.5 rounded-full bg-[#34C759]/10 px-3 py-1.5 transition-colors group-hover:bg-[#34C759]/20"
                    >
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
                      {{ t(getTypeLabelKey(loan.type)) }}
                    </span>
                  </td>
                </tr>

                <!-- Expanded Details Panel Row -->
                <tr v-if="expandedRowIndex === index" class="bg-[#F7F8FC]/30">
                  <td :colspan="columns.length + 1" class="px-4 py-6">
                    <LoanDetailsPanel :loan="convertToFullLoan(loan)" />
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Mobile/Tablet Card View (below md) -->
    <div class="md:hidden">
      <div v-if="loans.length === 0 && !loading" class="flex flex-col items-center justify-center py-12 px-4">
        <div
          class="flex h-16 w-16 items-center justify-center rounded-full bg-[#6B7280]/10 mb-3"
        >
          <svg
            class="w-8 h-8 text-[#6B7280]"
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
        <p class="text-base font-semibold text-[#111827] mb-1">
          {{ t(emptyMessage) }}
        </p>
        <p class="text-xs text-[#6B7280] text-center">
          {{ t(emptyDescription) }}
        </p>
      </div>

      <div v-else-if="loading" class="flex flex-col items-center justify-center py-12">
        <div
          class="h-10 w-10 animate-spin rounded-full border-4 border-[#007AFF] border-t-transparent mb-3"
        ></div>
        <p class="text-xs font-medium text-[#6B7280]">
          {{ t("loanList.messages.loading") }}
        </p>
      </div>

      <div v-else class="divide-y divide-[#E5E5EA]">
        <div
          v-for="(loan, index) in loans"
          :key="loan.id ?? index"
          class="px-4 py-4 sm:px-5 sm:py-5"
        >
          <!-- Card header: Borrower + Amount -->
          <button
            type="button"
            class="w-full text-left mb-4 focus:outline-none"
            @click="toggleRowExpand(index)"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="flex items-center gap-3 flex-1 min-w-0">
                <div
                  class="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-[#007AFF]/10"
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
                    class="text-sm font-semibold text-[#111827] truncate"
                    :dir="isRTL ? 'rtl' : 'ltr'"
                  >
                    {{ loan.borrower.name }}
                  </p>
                  <p
                    class="text-xs text-[#6B7280] truncate"
                    :dir="isRTL ? 'rtl' : 'ltr'"
                  >
                    {{ formatPhone(loan.borrower.phone) }}
                  </p>
                </div>
              </div>

              <!-- Amount Badge -->
              <div
                class="inline-flex items-center gap-1 rounded-full bg-[#34C759]/10 px-2.5 py-1.5 flex-shrink-0"
              >
                <span class="text-xs sm:text-sm font-semibold text-[#34C759]">
                  {{ formatCurrency(loan.amount) }}
                </span>
              </div>
            </div>
          </button>

          <!-- Card body: Key info -->
          <div class="space-y-3 mb-4">
            <!-- Email -->
            <div v-if="loan.borrower.email" class="flex items-start gap-2">
              <svg
                class="w-4 h-4 text-[#6B7280] flex-shrink-0 mt-0.5"
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
                class="text-xs sm:text-sm text-[#111827] break-all"
                :dir="isRTL ? 'rtl' : 'ltr'"
              >
                {{ loan.borrower.email }}
              </p>
            </div>

            <!-- Type -->
            <div class="flex items-center gap-2">
              <span
                :class="[
                  'inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs font-medium',
                  loan.type === 'checks'
                    ? 'bg-[#007AFF]/10 text-[#007AFF]'
                    : 'bg-[#FF9500]/10 text-[#FF9500]',
                ]"
              >
                {{ t(getTypeLabelKey(loan.type)) }}
              </span>
            </div>
          </div>

          <!-- Expand button -->
          <button
            type="button"
            class="w-full text-[#007AFF] text-xs font-semibold py-2 hover:bg-[#007AFF]/5 rounded-lg transition-colors flex items-center justify-center gap-1"
            @click="toggleRowExpand(index)"
          >
            <span>
            {{
              expandedRowIndex === index
              ? t("loanList.hideDetails")
              : t("loanList.showDetails")
            }}
            </span>

            <svg
              :class="[
                'w-4 h-4 transition-transform',
                expandedRowIndex === index ? 'rotate-180' : ''
              ]"
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

          <!-- Expanded Details -->
          <div v-if="expandedRowIndex === index" class="mt-4 pt-4 border-t border-[#E5E5EA]">
            <LoanDetailsPanel :loan="convertToFullLoan(loan)" />
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state (desktop) -->
    <div
      v-if="loans.length === 0 && !loading"
      class="hidden md:flex flex-col items-center justify-center py-16 px-4"
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
      class="hidden md:flex flex-col items-center justify-center py-16"
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
import { ref, computed } from "vue";
import type { LoanListItem, Loan } from "../types/loan";
import { LoanType } from "../types/loan";
import LoanDetailsPanel from "./loan-details/LoanDetailsPanel.vue";

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

const expandedRowIndex = ref<number | null>(null);

const columns = computed<Column[]>(() => [
  { key: "borrower", labelKey: "loanList.table.borrower", minWidth: "220px", icon: "user" },
  { key: "email", labelKey: "loanList.table.email", minWidth: "220px", icon: "email" },
  { key: "amount", labelKey: "loanList.table.amount", minWidth: "150px", icon: "amount" },
  { key: "type", labelKey: "loanList.table.type", minWidth: "150px", icon: "type" },
]);

const formatPhone = (phone: string): string => {
  if (!phone) return "—";
  const cleaned = phone.replace(/\D/g, "");
  if (cleaned.length === 10) {
    return cleaned.replace(/(\d{3})(\d{3})(\d{4})/, "$1-$2-$3");
  }
  return phone;
};

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat("he-IL", {
    style: "currency",
    currency: "ILS",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

const getTypeLabelKey = (type: LoanType): string => {
  return type === LoanType.CHECKS
    ? "loanList.types.checks"
    : "loanList.types.standingOrders";
};

const toggleRowExpand = (rowIndex: number) => {
  if (expandedRowIndex.value === rowIndex) {
    expandedRowIndex.value = null;
  } else {
    expandedRowIndex.value = rowIndex;
  }
};

const convertToFullLoan = (listItem: LoanListItem): Loan => {
  return {
    id: listItem.id,
    amount: listItem.amount,
    type: listItem.type,
    status: listItem.status,
    startDate: listItem.startDate,
    createdAt: listItem.borrower.createdAt ?? "",
    formFileUrl: undefined,
    borrower: {
      name: listItem.borrower.name,
      phone: listItem.borrower.phone,
      email: listItem.borrower.email,
      idNumber: listItem.borrower.idNumber,
      address: listItem.borrower.address,
      createdAt: listItem.borrower.createdAt,
    },
    trustee: listItem.trustee
      ? {
          name: listItem.trustee.name,
          community: listItem.trustee.community,
          phone: listItem.trustee.phone,
          notes: listItem.trustee.notes,
        }
      : null,
    details: {},
  } as Loan;
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
