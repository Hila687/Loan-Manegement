import { ref, computed, watch } from "vue";
import type { Ref, ComputedRef } from "vue";
import loanService from "../services/loanService";
import type { LoanListItem, LoanFilters } from "../types/loan";

/**
 * Composable for managing loans state and operations
 * Provides reactive state, fetch operations, and filtering capabilities
 */
export function useLoans() {
  // Reactive state
  const loans: Ref<LoanListItem[]> = ref([]);
  const loading = ref(false);
  const error: Ref<string | null> = ref(null);  
  const filters: Ref<LoanFilters> = ref(
    {
      type: "all",
      status: "active",
      search: undefined,
    } as LoanFilters
  );

  // Track if initial fetch has been done
  const initialFetchDone = ref(false);

  /**
   * Fetch loans from API with current filters
   */
  const fetchLoans = async () => {
    loading.value = true;
    error.value = null;

    try {
      const data = await loanService.getActiveLoans(filters.value);
      loans.value = data;
      initialFetchDone.value = true;

      if (import.meta.env.DEV) {
        console.log("[useLoans] Fetched", data.length, "loans", filters.value);
      }
    } catch (e: any) {
      console.error("[useLoans] Failed to fetch loans:", e);

      if (e?.response?.status === 404) {
        error.value =
          "Loans endpoint not found. Please check your API configuration.";
      } else if (e?.response?.status === 500) {
        error.value = "Server error. Please try again later.";
      } else if (e?.code === "ECONNABORTED") {
        error.value = "Request timeout. Please check your connection.";
      } else {
        error.value =
          e?.response?.data?.detail ||
          e?.message ||
          "Failed to load loans";
      }

      loans.value = [];
    } finally {
      loading.value = false;
    }
  };

  /**
   * Update a specific filter and refetch loans
   */
  const setFilter = (key: keyof LoanFilters, value: any) => {
    filters.value = { ...filters.value, [key]: value };

    if (import.meta.env.DEV) {
      console.log("[useLoans] Filter updated:", { [key]: value });
    }

    fetchLoans();
  };

  /**
   * Update multiple filters at once
   */
  const setFilters = (newFilters: Partial<LoanFilters>) => {
    filters.value = { ...filters.value, ...newFilters };

    if (import.meta.env.DEV) {
      console.log("[useLoans] Multiple filters updated:", newFilters);
    }

    fetchLoans();
  };

  /**
   * Reset all filters to default values
   */
  const resetFilters = () => {
    filters.value = {
      type: "all",
      status: "active",
      search: undefined,
    } as LoanFilters;

    if (import.meta.env.DEV) {
      console.log("[useLoans] Filters reset to default");
    }

    fetchLoans();
  };

  /**
   * Clear search filter only
   */
  const clearSearch = () => {
    filters.value = { ...filters.value, search: undefined };
    fetchLoans();
  };

  /**
   * Retry fetching after error
   */
  const retry = () => {
    if (import.meta.env.DEV) {
      console.log("[useLoans] Retrying fetch...");
    }
    fetchLoans();
  };

  /**
   * Refresh loans (force refetch)
   */
  const refresh = () => {
    if (import.meta.env.DEV) {
      console.log("[useLoans] Refreshing loans...");
    }
    fetchLoans();
  };

  // Computed properties
  const hasLoans = computed(() => loans.value.length > 0);

  const hasActiveFilters: ComputedRef<boolean> = computed(() => {
    return (
      filters.value.type !== "all" ||
      (filters.value.search != null && filters.value.search.length > 0)
    );
  });

  const totalAmount = computed(() => {
    return loans.value.reduce((sum, loan) => sum + (loan.amount || 0), 0);
  });

  const loansByType = computed(() => {
    const counts = {
      checks: 0,
      standing_orders: 0,
    };

    loans.value.forEach((loan) => {
      if (loan.type === "checks") {
        counts.checks++;
      } else if (loan.type === "standing_orders") {
        counts.standing_orders++;
      }
    });

    return counts;
  });

  const isLoading = computed(() => loading.value);
  const hasError = computed(() => error.value !== null);
  const isEmpty = computed(() => !loading.value && loans.value.length === 0);

  const filterSummary = computed(() => {
    const parts: string[] = [];

    if (filters.value.type && filters.value.type !== "all") {
      parts.push(`Type: ${filters.value.type}`);
    }

    if (filters.value.search) {
      parts.push(`Search: "${filters.value.search}"`);
    }

    return parts.length > 0 ? parts.join(", ") : "No filters";
  });

  // Debug
  if (import.meta.env.DEV) {
    watch(
      filters,
      (newFilters) => {
        console.log("[useLoans] Filters changed:", newFilters);
      },
      { deep: true }
    );
  }

  return {
    // State
    loans,
    loading,
    error,
    filters,
    initialFetchDone,

    // Computed
    hasLoans,
    hasActiveFilters,
    totalAmount,
    loansByType,
    isLoading,
    hasError,
    isEmpty,
    filterSummary,

    // Methods
    fetchLoans,
    setFilter,
    setFilters,
    resetFilters,
    clearSearch,
    retry,
    refresh,
  };
}

export type UseLoansReturn = ReturnType<typeof useLoans>;
