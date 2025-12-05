<!-- src/pages/LoanList.vue -->
<template>
  <AppLayout>
    <div class="flex justify-between items-center mb-4">
      <h1 class="text-2xl font-bold">{{ t("loan.activeLoans") }}</h1>
    </div>

    <LoanTypeFilter v-model="loanType" />

    <div class="mt-4">
      <LoanTable />

      <div v-if="loading" class="text-gray-500 mt-4">Loading...</div>
      <div v-if="error" class="text-red-600 mt-4">{{ error }}</div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { useI18n } from "vue-i18n";

import AppLayout from "../components/AppLayout.vue";
import LoanTable from "../components/LoanTable.vue";
import LoanTypeFilter from "../components/LoanTypeFilter.vue";

import { useLoans } from "../composables/useLoans";
import { useLoanFilters } from "../composables/useLoanFilters";

const { t } = useI18n();

const { loans, loadLoans, loading, error } = useLoans();
const { loanType } = useLoanFilters();

onMounted(() => {
  loadLoans();
});
</script>
