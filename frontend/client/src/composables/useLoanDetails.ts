// src/composables/useLoanDetails.ts
import { ref } from "vue";

export function useLoanDetails() {
  // Holds the ID of the currently opened loan row (null = no row is open)
  const openLoanId = ref<number | null>(null);

  // Toggles a loan row open/closed
  function toggleLoan(id: number) {
    // If this row is already open → close it
    if (openLoanId.value === id) {
      openLoanId.value = null;
    }
    // Otherwise → open this row
    else {
      openLoanId.value = id;
    }
  }

  // Returns true if the given row should be displayed as open
  function isOpen(id: number) {
    return openLoanId.value === id;
  }

  return {
    openLoanId,
    toggleLoan,
    isOpen,
  };
}
