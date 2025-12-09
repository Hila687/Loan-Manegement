<!-- src/components/loan-details/LoanInfoSection.vue -->
<template>
  <div class="space-y-2">
    <h2 class="text-lg font-semibold">{{ t("loanDetails.loanInfo") }}</h2>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-gray-700">

      <!-- Loan ID -->
      <div v-if="loan.loan_id">
        <strong>{{ t("loanDetails.loanId") }}</strong> {{ loan.loan_id }}
      </div>

      <!-- Amount -->
      <div>
        <strong>{{ t("loanDetails.amount") }}</strong> {{ formatAmount(loan.amount) }}
      </div>

      <!-- Loan Type -->
      <div>
        <strong>{{ t("loanDetails.loanType") }}</strong> {{ loan.loan_type }}
      </div>

      <!-- Start Date -->
      <div v-if="loan.start_date">
        <strong>{{ t("loanDetails.startDate") }}</strong> {{ formatDate(loan.start_date) }}
      </div>

      <!-- Status -->
      <div v-if="loan.status">
        <strong>{{ t("loanDetails.status") }}</strong> {{ loan.status }}
      </div>

      <!-- Created At -->
      <div v-if="loan.created_at">
        <strong>{{ t("loanDetails.createdAt") }}</strong> {{ formatDate(loan.created_at) }}
      </div>

      <!-- Form File -->
      <div v-if="loan.form_file_url">
        <strong>{{ t("loanDetails.formFile") }}</strong>
        <a :href="loan.form_file_url" target="_blank" class="text-blue-600 underline">
          {{ t("loanDetails.openForm") }}
        </a>
      </div>

      <!-- Trustee Info -->
      <div v-if="loan.trustee">
        <strong>{{ t("loanDetails.trustee") }}</strong> {{ loan.trustee.name }}
      </div>
      <div v-if="loan.trustee?.community">
        <strong>{{ t("loanDetails.trusteeCommunity") }}</strong> {{ loan.trustee.community }}
      </div>
      <div v-if="loan.trustee?.phone">
        <strong>{{ t("loanDetails.trusteePhone") }}</strong> {{ loan.trustee.phone }}
      </div>
      <div v-if="loan.trustee?.notes">
        <strong>{{ t("loanDetails.trusteeNotes") }}</strong> {{ loan.trustee.notes }}
      </div>

      <!-- Details: Checks -->
      <template v-if="loan.details && loan.loan_type === 'checks'">
        <div>
          <strong>{{ t("loanDetails.numPayments") }}</strong> {{ loan.details.num_payments }}
        </div>
        <div>
          <strong>{{ t("loanDetails.checkDetails") }}</strong> {{ loan.details.check_details }}
        </div>
        <div>
          <strong>{{ t("loanDetails.predefinedSchedule") }}</strong>
          {{ loan.details.predefined_schedule ? t("general.yes") : t("general.no") }}
        </div>
      </template>

      <!-- Details: Standing Order -->
      <template v-if="loan.details && loan.loan_type === 'standing'">
        <div>
          <strong>{{ t("loanDetails.monthlyAmount") }}</strong> {{ loan.details.monthly_amount }}
        </div>
        <div>
          <strong>{{ t("loanDetails.chargeDay") }}</strong> {{ loan.details.charge_day }}
        </div>
        <div>
          <strong>{{ t("loanDetails.stopDate") }}</strong>
          {{ loan.details.stop_date ? formatDate(loan.details.stop_date) : "-" }}
        </div>
      </template>

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

function formatAmount(amount: number) {
  return new Intl.NumberFormat("he-IL").format(amount) + " ₪";
}

function formatDate(date: string) {
  return new Date(date).toLocaleDateString("he-IL");
}
</script>
