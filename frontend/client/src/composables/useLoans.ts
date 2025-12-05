// src/composables/useLoans.ts
import { ref } from "vue";
import loanService from "../services/loanService";
import type { Loan } from "../types/loan";

export function useLoans() {
  const loans = ref<Loan[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function loadLoans(type: string = "all") {
    loading.value = true;
    error.value = null;

    try {
      loans.value = await loanService.getLoans(type);
    } catch (e: any) {
      error.value = e.message || "Failed to load loans";
    } finally {
      loading.value = false;
    }
  }

  return {
    loans,
    loading,
    error,
    loadLoans,
  };
}
