<template>
  <div class="rounded-lg border bg-white shadow p-4 space-y-6">

    <TabsSection @tab-change="handleTabChange">
      <template #details>

        <!-- Borrower Info Section -->
        <section>
          <BorrowerInfoSection :borrower="loan.borrower" />
        </section>

        <div class="border-t border-gray-200 my-6" />

        <!-- Loan Info Section -->
        <section>
          <h2 class="text-lg font-semibold mb-2">
            {{ t("loanDetails.loanInfo") }}
          </h2>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-gray-700">
            
            <!-- Loan Type -->
            <div>
              <strong>{{ t("loanDetails.type") }}</strong> {{ loan.type === "checks" ? "צ'קים" : "הוראת קבע" }}
            </div>

            <!-- Amount -->
            <div>
              <strong>{{ t("loanDetails.amount") }}</strong> {{ formatCurrency(loan.amount) }}
            </div>

            <!-- Status -->
            <div>
              <strong>{{ t("loanDetails.status") }}</strong> {{ loan.status }}
            </div>

            <!-- Start Date -->
            <div>
              <strong>{{ t("loanDetails.startDate") }}</strong> {{ formatDate(loan.startDate) }}
            </div>

            <!-- Created At -->
            <div>
              <strong>{{ t("loanDetails.createdAt") }}</strong> {{ formatDate(loan.createdAt) }}
            </div>

            <!-- Payment Details (for checks type) -->
            <template v-if="loan.type === 'checks' && loan.details">
              <!-- Number of Payments -->
              <div>
                <strong>{{ t("loanDetails.numPayments") }}</strong> {{ (loan.details as any).numPayments ?? "-" }}
              </div>

              <!-- Predefined Schedule -->
              <div>
                <strong>{{ t("loanDetails.predefinedSchedule") }}</strong> {{ (loan.details as any).predefinedSchedule ? t("loanDetails.yes") : t("loanDetails.no") }}
              </div>

              <!-- Check Details -->
              <div>
                <strong>{{ t("loanDetails.checkDetails") }}</strong> {{ (loan.details as any).checkDetails || "-" }}
              </div>
            </template>

            <!-- Payment Details (for standing order type) -->
            <template v-else-if="loan.type === 'standing_order' && loan.details">
              <!-- Monthly Amount -->
              <div>
                <strong>{{ t("loanDetails.monthlyAmount") }}</strong> {{ formatCurrency((loan.details as any).monthlyAmount) }}
              </div>

              <!-- Charge Day -->
              <div>
                <strong>{{ t("loanDetails.chargeDay") }}</strong> {{ (loan.details as any).chargeDay ?? "-" }}
              </div>

              <!-- Stop Date -->
              <div>
                <strong>{{ t("loanDetails.stopDate") }}</strong> {{ (loan.details as any).stopDate || "-" }}
              </div>
            </template>

          </div>
        </section>

        <div class="border-t border-gray-200 my-6" />

        <!-- Trustee Section -->
        <section v-if="loan.trustee">
          <h2 class="text-lg font-semibold mb-2">
            {{ t("loanDetails.trustee") }}
          </h2>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm text-gray-700">
            
            <!-- Name -->
            <div>
              <strong>{{ t("loanDetails.name") }}</strong> {{ loan.trustee.name || "-" }}
            </div>

            <!-- Phone -->
            <div>
              <strong>{{ t("loanDetails.phone") }}</strong> <span dir="ltr" class="text-right inline-block w-full sm:w-auto text-left">{{ loan.trustee.phone || "-" }}</span>
            </div>

            <!-- Community -->
            <div>
              <strong>{{ t("loanDetails.community") }}</strong> {{ loan.trustee.community || "-" }}
            </div>

            <!-- Notes -->
            <div>
              <strong>{{ t("loanDetails.notes") }}</strong> 
              <span v-if="loan.trustee.notes" class="bg-yellow-50 px-2 py-0.5 rounded text-gray-800">{{ loan.trustee.notes }}</span>
              <span v-else>-</span>
            </div>

          </div>
        </section>

      </template>

      <template #schedule>
        <PaymentScheduleTab :loanId="loan.id" :active="activeTab === 'schedule'" />
      </template>

    </TabsSection>

    <div class="pt-4 border-t flex justify-end">
      <EditLoanButton :loanId="loan.id" />
    </div>

  </div>
</template>

<script setup lang="ts">
import type { Loan } from "../../types/loan";
import { useI18n } from "vue-i18n";
import { ref } from "vue";

import BorrowerInfoSection from "./BorrowerInfoSection.vue";
import TabsSection from "./TabsSection.vue";
import EditLoanButton from "./EditLoanButton.vue";
import PaymentScheduleTab from "./PaymentScheduleTab.vue";

const { t } = useI18n();
const activeTab = ref<"details" | "schedule">("details");

defineProps<{
  loan: Loan;
}>();

function formatCurrency(amount: number) {
  return new Intl.NumberFormat("he-IL", {
    style: "currency",
    currency: "ILS",
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatDate(date?: string) {
  return date ? new Date(date).toLocaleDateString("he-IL") : "-";
}

function handleTabChange(tab: "details" | "schedule") {
  activeTab.value = tab;
}
</script>