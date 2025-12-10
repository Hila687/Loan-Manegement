<!-- src/components/loan-details/LoanInfoSection.vue -->
<template>
  <div class="space-y-2">
    <h2 class="text-lg font-semibold">{{ t("loanDetails.loanInfo") }}</h2>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-gray-700">

      <!-- Amount -->
      <div>
        <strong>{{ t("loanDetails. amount") }}</strong>
        {{ formatCurrency(loan.amount) }}
      </div>

      <!-- Type -->
      <div>
        <strong>{{ t("loanDetails.type") }}</strong>
        {{ loan.type === "checks" ?  "צ'קים" : "הוראות קבע" }}
      </div>

      <!-- Status -->
      <div>
        <strong>{{ t("loanDetails.status") }}</strong>
        {{ loan.status || "פעיל" }}
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import type { Loan } from "../../types/loan";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const props = defineProps<{
  loan: Loan;
}>();

function formatCurrency(amount: number) {
  return new Intl.NumberFormat("he-IL", {
    style: "currency",
    currency: "ILS",
  }).format(amount);
}
</script>