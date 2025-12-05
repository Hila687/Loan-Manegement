// src/composables/useLoanFilters.ts
import { ref } from "vue";

export function useLoanFilters() {
  const loanType = ref("all");

  function setLoanType(type: string) {
    loanType.value = type;
  }

  return { loanType, setLoanType };
}
