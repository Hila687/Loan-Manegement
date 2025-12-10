<!-- src/pages/LoanDetailsPage. vue -->
<template>
  <AppLayout
    :title="t('loanDetails.title')"
    :subtitle="loan?. borrower?.name || ''"
    :show-back-button="true"
    :show-language-toggle="true"
  >
    <div v-if="loading" class="flex items-center justify-center py-16">
      <div class="h-12 w-12 animate-spin rounded-full border-4 border-[#007AFF] border-t-transparent mb-4"></div>
      <p class="text-sm font-medium text-[#6B7280]">{{ t("loanList.messages.loading") }}</p>
    </div>

    <div v-else-if="loan" class="space-y-6">
      <LoanDetailsPanel :loan="loan" />
    </div>

    <div v-else class="text-center py-16">
      <p class="text-lg text-[#6B7280]">{{ t('loanDetails.notFound') }}</p>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { useI18n } from "vue-i18n";
import AppLayout from "../components/AppLayout.vue";
import LoanDetailsPanel from "../components/loan-details/LoanDetailsPanel.vue";
import type { Loan } from "../types/loan";

const { t } = useI18n();
const route = useRoute();
const loanId = route.params.id as string;

const loan = ref<Loan | null>(null);
const loading = ref(false);

onMounted(async () => {
  loading.value = true;
  try {
    // TODO: Fetch loan details from API
    // const response = await loanService.getLoanById(parseInt(loanId));
    // loan.value = response;
    console.log("Loading loan details for ID:", loanId);
  } catch (error) {
    console.error("Failed to load loan:", error);
  } finally {
    loading.value = false;
  }
});
</script>