<!-- src/components/loan-details/LoanDetailsPanel.vue -->
<template>
  <div class="rounded-lg border bg-white shadow p-4 space-y-6">

    <!-- ============================= -->
    <!-- Tabs Section (translated)    -->
    <!-- ============================= -->
    <TabsSection
      :labels="{
        details: t('loanDetails.tabDetails'),
        schedule: t('loanDetails.tabSchedule')
      }"
    >

      <!-- Details tab -->
      <template #details>
        <section>
          <BorrowerInfoSection :borrower="loan.borrower" />
        </section>

        <section>
          <LoanInfoSection :loan="loan" />
        </section>
      </template>

      <!-- (Future) Payment Schedule Tab -->
      <template #schedule>
        <div class="text-gray-500 text-center py-4">
          {{ t("loanDetails.schedulePlaceholder") }}
        </div>
      </template>

    </TabsSection>

    <!-- ============================= -->
    <!-- Edit Loan Button             -->
    <!-- ============================= -->
    <div class="pt-4 border-t">
      <EditLoanButton :loanId="loan.id" />
    </div>

  </div>
</template>

<script setup lang="ts">
import type { Loan } from "../../types/loan";

import { useI18n } from "vue-i18n";
const { t } = useI18n();

import BorrowerInfoSection from "./BorrowerInfoSection.vue";
import LoanInfoSection from "./LoanInfoSection.vue";
import TabsSection from "./TabsSection.vue";
import EditLoanButton from "./EditLoanButton.vue";

const props = defineProps<{
  loan: Loan;
}>();
</script>

<style scoped>
</style>
