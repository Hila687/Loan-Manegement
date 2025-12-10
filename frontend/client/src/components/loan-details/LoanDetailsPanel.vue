<!-- frontend/client/src/components/loan-details/LoanDetailsPanel.vue -->
<template>
  <div
    class="w-full rounded-2xl border border-[#E5E5EA] bg-white shadow-sm px-3 py-4 sm:px-6 sm:py-6 lg:px-8 lg:py-7"
    :dir="isRTL ? 'rtl' : 'ltr'"
  >
    <!-- Tabs only -->
    <div class="flex border-b border-[#E5E5EA] mb-4 sm:mb-6 -mx-3 sm:mx-0 px-3 sm:px-0">
      <button
        type="button"
        class="px-2 sm:px-4 py-2 text-xs sm:text-sm font-medium border-b-2 whitespace-nowrap"
        :class="
          activeTab === 'details'
            ? 'border-[#007AFF] text-[#007AFF]'
            : 'border-transparent text-[#6B7280] hover:text-[#111827]'
        "
        @click="activeTab = 'details'"
      >
        {{ t("loanDetails.tabDetails") }}
      </button>
      <button
        type="button"
        class="px-2 sm:px-4 py-2 text-xs sm:text-sm font-medium border-b-2 whitespace-nowrap"
        :class="
          activeTab === 'schedule'
            ? 'border-[#007AFF] text-[#007AFF]'
            : 'border-transparent text-[#6B7280] hover:text-[#111827]'
        "
        @click="activeTab = 'schedule'"
      >
        {{ t("loanDetails.tabSchedule") }}
      </button>
    </div>

    <!-- Details Tab -->
    <div v-if="activeTab === 'details'" class="space-y-6">
      <!-- Borrower Info Section -->
      <section>
        <h3
          class="text-xs font-semibold text-[#6B7280] uppercase tracking-wide mb-4"
          :class="isRTL ? 'text-right' : 'text-left'"
        >
          {{ t("loanDetails.borrowerInfo") }}
        </h3>
        <div class="space-y-3">
          <InfoRow
            :label="t('loanDetails.name')"
            :value="loan.borrower?.name || '—'"
            :is-rtl="isRTL"
          />
          <InfoRow
            :label="t('loanDetails.phone')"
            :value="formatPhone(loan.borrower?.phone)"
            :is-rtl="isRTL"
          />
          <InfoRow
            :label="t('loanDetails.email')"
            :value="loan.borrower?.email || '—'"
            :is-rtl="isRTL"
          />
          <!-- NEW: borrower address -->
          <InfoRow
            :label="t('loanDetails.address')"
            :value="loan.borrower?.address || '—'"
            :is-rtl="isRTL"
          />
          <!-- NEW: trustee shown inside borrower details -->
          <InfoRow
            :label="t('loanDetails.trustee')"
            :value="loan.trustee?.name || '—'"
            :is-rtl="isRTL"
          />
        </div>
      </section>

      <!-- Loan Info Section -->
      <section class="pt-6 border-t border-[#E5E5EA]">
        <h3
          class="text-xs font-semibold text-[#6B7280] uppercase tracking-wide mb-4"
          :class="isRTL ? 'text-right' : 'text-left'"
        >
          {{ t("loanDetails.loanInfo") }}
        </h3>
        <div class="space-y-3">
          <InfoRow
            :label="t('loanDetails.type')"
            :value="t(getTypeLabelKey(loan.type))"
            :is-rtl="isRTL"
          />
          <InfoRow
            :label="t('loanDetails.amount')"
            :value="formatCurrency(loan.amount)"
            :is-rtl="isRTL"
            :highlight="true"
          />
          <InfoRow
            :label="t('loanDetails.status')"
            :value="loan.status"
            :is-rtl="isRTL"
          />
        </div>
      </section>

      <!-- Trustee Info (if available) -->
      <section v-if="loan.trustee?.name" class="pt-6 border-t border-[#E5E5EA]">
        <h3
          class="text-xs font-semibold text-[#6B7280] uppercase tracking-wide mb-4"
          :class="isRTL ? 'text-right' : 'text-left'"
        >
          {{ t("loanDetails.trustee") || "Trustee" }}
        </h3>
        <div class="space-y-3">
          <InfoRow
            :label="t('loanDetails.trustee')"
            :value="loan.trustee.name"
            :is-rtl="isRTL"
          />
          <InfoRow
            v-if="loan.trustee.community"
            :label="t('loanDetails.community') || 'Community'"
            :value="loan.trustee.community"
            :is-rtl="isRTL"
          />
        </div>
      </section>
    </div>

    <!-- Schedule Tab -->
    <div v-else class="py-4">
      <p
        class="text-sm text-[#6B7280]"
        :class="isRTL ? 'text-right' : 'text-left'"
      >
        {{ t("loanDetails.tabSchedule") }} – coming soon.
      </p>
    </div>

    <!-- Edit Button -->
    <div
      class="mt-8 flex justify-end"
      :class="isRTL ? 'flex-row-reverse' : 'flex-row'"
    >
      <button
        type="button"
        class="inline-flex items-center justify-center rounded-xl px-5 py-2.5 text-sm font-medium text-white bg-[#007AFF] hover:bg-[#0060D1] active:bg-[#0051BA] transition-colors shadow-sm"
        @click="$emit('edit', loan)"
      >
        {{ t("loanDetails.editButton") }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import type { Loan, LoanType } from "../../types/loan";
import { useLocale } from "../../composables/useLocale";
import InfoRow from "./InfoRow.vue";

interface Props {
  loan: Loan;
}

const { loan } = defineProps<Props>();

// Locale helper
const { t, isRTL } = useLocale();

// Local tab state
const activeTab = ref<"details" | "schedule">("details");

/**
 * Format phone number for display.
 */
const formatPhone = (phone?: string): string => {
  if (!phone) return "—";
  const cleaned = phone.replace(/\D/g, "");
  if (cleaned.length === 10) {
    return cleaned.replace(/(\d{3})(\d{3})(\d{4})/, "$1-$2-$3");
  }
  return phone;
};

/**
 * Format numeric amount as ILS currency with no decimals.
 */
const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat("he-IL", {
    style: "currency",
    currency: "ILS",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
};

/**
 * Map loan type to i18n key.
 */
const getTypeLabelKey = (type: LoanType): string => {
  return type === "checks"
    ? "loanList.types.checks"
    : "loanList.types.standingOrders";
};
</script>

<style scoped>
button {
  transition: all 0.2s ease;
}

button:active {
  transform: scale(0.98);
}
</style>
