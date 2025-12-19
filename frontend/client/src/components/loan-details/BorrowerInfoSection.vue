<!-- src/components/loan-details/BorrowerInfoSection.vue -->
<template>
  <div class="space-y-2">
    <h2 class="text-lg font-semibold">{{ t("loanDetails.borrowerInfo") }}</h2>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-gray-700">

      <div>
        <strong>{{ t("loanDetails.name") }}</strong> {{ borrower.name || "-" }}
      </div>

      <div>
        <strong>{{ t("loanDetails.phone") }}</strong> {{ borrower.phone || "-" }}
      </div>

      <div>
        <strong>{{ t("loanDetails.email") }}</strong> {{ borrower.email || "-" }}
      </div>

      <div>
        <strong>{{ t("loanDetails.address") }}</strong> {{ borrower.address || "-" }}
      </div>

      <div>
        <strong>{{ t("loanDetails.idNumber") }}</strong> {{ borrower.idNumber || "-" }}
      </div>

      <div>
        <strong>{{ t("loanDetails.createdAt") }}</strong>
        {{ formatDate(borrower.createdAt) }}
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import type { Borrower } from "../../types/loan";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

defineProps<{ borrower: Borrower }>();

function formatDate(date?: string) {
  return date ? new Date(date).toLocaleDateString("he-IL") : "-";
}
</script>
