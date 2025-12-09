<!-- src/components/loan-details/BorrowerInfoSection.vue -->
<template>
  <div class="space-y-2">
    <h2 class="text-lg font-semibold">{{ t("loanDetails.borrowerInfo") }}</h2>

    <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-gray-700">

      <!-- Name -->
      <div>
        <strong>{{ t("loanDetails.name") }}</strong> {{ borrower.name || "-" }}
      </div>

      <!-- Phone -->
      <div>
        <strong>{{ t("loanDetails.phone") }}</strong> {{ borrower.phone || "-" }}
      </div>

      <!-- Email -->
      <div>
        <strong>{{ t("loanDetails.email") }}</strong> {{ borrower.email || "-" }}
      </div>

      <!-- ID Number -->
      <div v-if="borrower.id_number">
        <strong>{{ t("loanDetails.idNumber") }}</strong> {{ borrower.id_number }}
      </div>

      <!-- Address -->
      <div v-if="borrower.address">
        <strong>{{ t("loanDetails.address") }}</strong> {{ borrower.address }}
      </div>

      <!-- Created At -->
      <div v-if="borrower.created_at">
        <strong>{{ t("loanDetails.createdAt") }}</strong> {{ formatDate(borrower.created_at) }}
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import type { Borrower } from "../../types/loan";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const props = defineProps<{
  borrower: Borrower;
}>();

function formatDate(date: string) {
  return new Date(date).toLocaleDateString("he-IL");
}
</script>
