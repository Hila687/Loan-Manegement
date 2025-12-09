<!-- src/components/LoanTable.vue -->
<template>
  <div class="bg-white shadow rounded-lg overflow-hidden">
    <table
      class="w-full text-sm"
      :class="locale === 'he' ? 'text-right' : 'text-left'"
      :dir="locale === 'he' ? 'rtl' : 'ltr'"
    >
      <thead class="bg-gray-100 text-gray-700">
        <tr>
          <th class="p-3 w-6"></th>

          <th class="p-3">{{ t("loanTable.borrower") }}</th>
          <th class="p-3">{{ t("loanTable.phone") }}</th>
          <th class="p-3">{{ t("loanTable.email") }}</th>
          <th class="p-3">{{ t("loanTable.trustee") }}</th>
          <th class="p-3">{{ t("loanTable.amount") }}</th>
        </tr>
      </thead>

      <tbody>
        <LoanRow
          v-for="loan in loans"
          :key="loan.loan_id"
          :loan="loan"
          :open="openLoanId === loan.loan_id"
          @click-row="$emit('row-click', loan.loan_id)"
          @close-row="$emit('row-close')"
        />
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import LoanRow from "./loan-details/LoanRow.vue";
import type { Loan } from "../types/loan";
import { useI18n } from "vue-i18n";

const { t, locale } = useI18n();

defineProps<{
  loans: Loan[];
  openLoanId: string | number | null;
}>();

defineEmits(["row-click", "row-close"]);
</script>
