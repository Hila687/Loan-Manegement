<!-- src/components/loan-details/EditLoanButton.vue -->
<template>
  <button
    @click="goToEdit"
    class="w-full px-4 py-2.5 rounded-lg bg-[#007AFF] text-white font-semibold transition-all hover:bg-[#0051D5] active:scale-95"
  >
    {{ t("loanDetails.editButton") }}
  </button>
</template>

<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";

const { t } = useI18n();
const router = useRouter();

const props = defineProps<{
  loanId: number;
}>();

const goToEdit = () => {
  router.push(`/loans/${props.loanId}/edit`);
};
</script>