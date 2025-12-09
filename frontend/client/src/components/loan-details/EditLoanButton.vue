<!-- src/components/loan-details/EditLoanButton.vue -->
<template>
  <button
    type="button"
    class="inline-flex items-center gap-2 rounded-lg border border-[#007AFF]
           px-4 py-2 text-sm font-medium text-[#007AFF]
           hover:bg-[#007AFF]/5 transition-colors"
    @click="goToEdit"
  >
    <!-- Simple edit icon -->
    <svg
      class="w-4 h-4"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M11 5h2m-1 0v14m-7-4h14"
      />
    </svg>
    <span>{{ t("loanDetails.actions.editLoan") }}</span>
  </button>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";
import { useI18n } from "vue-i18n";

const { t } = useI18n();
const router = useRouter();

// Accept loanId as string, matching Loan.id type
const props = defineProps<{
  loanId: string;
}>();

// Navigate to loan edit page (route can be adjusted if needed)
const goToEdit = () => {
  router.push(`/loans/${props.loanId}/edit`);
};
</script>

<style scoped>
</style>
