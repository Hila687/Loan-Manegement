<!-- src/components/loan-details/LoanRow.vue -->
<template>
  <tr class="hover:bg-gray-50 cursor-pointer" @click="onClickRow">
    
    <!-- אייקון פתיחה/סגירה -->
    <td class="p-4 w-6 text-gray-500 text-lg select-none">
      {{ isOpen(loan.loan_id) ? "▲" : "▼" }}
    </td>

    <!-- Borrower -->
    <td class="p-4" :class="textDirClass">
      {{ loan.borrower.name }}
    </td>

    <!-- Phone -->
    <td class="p-4" :class="textDirClass">
      {{ loan.borrower.phone }}
    </td>

    <!-- Email -->
    <td class="p-4" :class="textDirClass">
      {{ loan.borrower.email || "-" }}
    </td>

    <!-- Trustee -->
    <td class="p-4" :class="textDirClass">
      {{ loan.trustee.name }}
    </td>

    <!-- Amount -->
    <td class="p-4" :class="textDirClass">
      {{ formatAmount(loan.amount) }}
    </td>
  </tr>

  <!-- Expanded Row -->
  <tr v-if="isOpen(loan.loan_id)">
    <td colspan="6" class="bg-gray-50 p-4 border-t">
      <LoanDetailsPanel :loan="loan" />
    </td>
  </tr>
</template>

<script setup lang="ts">
import { watch, computed } from "vue";
import { useI18n } from "vue-i18n";
import type { Loan } from "../../types/loan";

import LoanDetailsPanel from "./LoanDetailsPanel.vue";
import { useLoanDetails } from "../../composables/useLoanDetails";

const props = defineProps<{
  loan: Loan,
  open?: boolean
}>();

const emit = defineEmits(["click-row", "close-row"]);

const { toggleLoan, isOpen } = useLoanDetails();
const { locale } = useI18n();

/* RTL/LTR text alignment */
const textDirClass = computed(() => {
  return locale.value === "he" ? "text-right" : "text-left";
});

// Sync URL → row open/close
watch(
  () => props.open,
  (shouldOpen) => {
    const now = isOpen(props.loan.loan_id);
    if (shouldOpen && !now) toggleLoan(props.loan.loan_id);
    if (!shouldOpen && now) toggleLoan(props.loan.loan_id);
  },
  { immediate: true }
);

// clicking row toggles open/close + notifies parent
function onClickRow() {
  const now = isOpen(props.loan.loan_id);
  if (!now) emit("click-row", props.loan.loan_id);
  else emit("close-row");
}

function formatAmount(amount: number) {
  return new Intl.NumberFormat("he-IL").format(amount) + " ₪";
}
</script>
