<!-- src/components/loan-details/LoanInfoSection.vue -->
<template>
  <div class="space-y-2">
    <h2 class="text-lg font-semibold">{{ t("loanDetails.loanInfo") }}</h2>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-gray-700">

      <div>
        <strong>{{ t("loanDetails.loanId") }}</strong> {{ loan.id }}
      </div>

      <div>
        <strong>{{ t("loanDetails.type") }}</strong>
        {{ loan.type === "checks" ? "צ'קים" : "הוראת קבע" }}
      </div>

      <div>
        <strong>{{ t("loanDetails.amount") }}</strong>
        {{ formatCurrency(loan.amount) }}
      </div>

      <div>
        <strong>{{ t("loanDetails.status") }}</strong> {{ loan.status }}
      </div>

      <div>
        <strong>{{ t("loanDetails.startDate") }}</strong>
        {{ formatDate(loan.startDate) }}
      </div>

      <div>
        <strong>{{ t("loanDetails.createdAt") }}</strong>
        {{ formatDate(loan.createdAt) }}
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import type { Loan } from "../../types/loan";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

defineProps<{ loan: Loan }>();

function formatCurrency(amount: number) {
  return new Intl.NumberFormat("he-IL", {
    style: "currency",
    currency: "ILS",
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatDate(date?: string) {
  return date ? new Date(date).toLocaleDateString("he-IL") : "-";
}
</script>
