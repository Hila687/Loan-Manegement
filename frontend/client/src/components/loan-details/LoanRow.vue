<!-- frontend/client/src/components/loan-details/LoanRow.vue -->
<template>
  <tr class="hover:bg-gray-50 cursor-pointer" @click="onClickRow">
    <!-- Open/close icon -->
    <td class="p-4 w-6 text-gray-500 text-lg select-none">
      {{ isOpen(loan.id) ? "▲" : "▼" }}
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
      {{ loan.trustee?.name || "-" }}
    </td>

    <!-- Amount -->
    <td class="p-4" :class="textDirClass">
      {{ formatAmount(loan.amount) }}
    </td>
  </tr>

  <!-- Expanded Row -->
  <tr v-if="isOpen(loan.id)">
    <td colspan="6" class="bg-gray-50 p-4 border-t">
      <LoanDetailsPanel :loan="loan" />
    </td>
  </tr>
</template>

<script setup lang="ts">
import { watch, computed } from "vue";
import type { Loan } from "../../types/loan";
import LoanDetailsPanel from "./LoanDetailsPanel.vue";
import { useLoanDetails } from "../../composables/useLoanDetails";
import { useLocale } from "../../composables/useLocale";

const props = defineProps<{
  loan: Loan;
  open?: boolean;
}>();

const emit = defineEmits<{
  (e: "click-row", id: string): void;
  (e: "close-row"): void;
}>();

const { isRTL } = useLocale();
const { toggleLoan, isOpen } = useLoanDetails();

/**
 * Direction-aware text alignment class
 */
const textDirClass = computed(() =>
  isRTL.value ? "text-right" : "text-left"
);

/**
 * Sync external `open` prop (if used) with internal open state
 */
watch(
  () => props.open,
  (shouldOpen) => {
    if (shouldOpen === undefined) return;
    const now = isOpen(props.loan.id);
    if (shouldOpen && !now) toggleLoan(props.loan.id);
    if (!shouldOpen && now) toggleLoan(props.loan.id);
  },
  { immediate: true }
);

/**
 * Toggle row open/close on click and notify parent
 */
function onClickRow() {
  const now = isOpen(props.loan.id);
  if (!now) {
    toggleLoan(props.loan.id);
    emit("click-row", props.loan.id);
  } else {
    toggleLoan(props.loan.id);
    emit("close-row");
  }
}

/**
 * Format amount with ILS locale
 */
function formatAmount(amount: number) {
  return new Intl.NumberFormat("he-IL").format(amount) + " ₪";
}
</script>
