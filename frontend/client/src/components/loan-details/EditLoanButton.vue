<!-- src/components/loan-details/EditLoanButton.vue -->
<template>
  <button
    @click="goToEdit"
    class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
  >
    {{ t("loanDetails.editLoan") }}
  </button>
</template>

<script setup lang="ts">
/**
 * EditLoanButton.vue
 * A reusable button that navigates to /loans/:id/edit.
 */

import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";

// תרגום
const { t } = useI18n();

// Props: loanId must be passed from parent component
const props = defineProps<{
  loanId: number;
}>();

const router = useRouter();

/**
 * Navigate to the edit loan page.
 */
function goToEdit() {
  router.push(`/loans/${props.loanId}/edit`);
}
</script>

<style scoped>
/* Optional styling */
</style>
