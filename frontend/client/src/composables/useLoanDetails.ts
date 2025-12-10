// frontend/client/src/composables/useLoanDetails.ts
import { ref } from "vue";

const openLoanId = ref<string | null>(null);

export function useLoanDetails() {
  const toggleLoan = (id: string) => {
    if (openLoanId.value === id) {
      openLoanId.value = null;
    } else {
      openLoanId.value = id;
    }
  };

  const isOpen = (id: string): boolean => {
    return openLoanId.value === id;
  };

  return {
    openLoanId,
    toggleLoan,
    isOpen,
  };
}
