import { ref, computed, watch } from "vue";
import type { Ref } from "vue";
import { LoanType } from "../types/loan";

/**
 * Composable for managing loan filter UI state
 * Handles dropdown state, search queries, and filter options
 * Separate from useLoans to maintain single responsibility
 */
export function useLoanFilters() {
  // Reactive state
  const selectedType: Ref<LoanType | "all"> = ref("all");
  const searchQuery = ref("");
  const isFilterDropdownOpen = ref(false);

  // Debounce timer for search
  let searchDebounceTimer: ReturnType<typeof setTimeout> | null = null;
  const debouncedSearchQuery = ref("");

  /**
   * Filter type options for dropdown
   * These map to translation keys
   */
  const filterOptions = computed(() => [
    {
      value: "all" as const,
      labelKey: "loanList.filters.all",
      icon: "all",
      description: "Show all loan types",
    },
    {
      value: LoanType.CHECKS,
      labelKey: "loanList.filters.checks",
      icon: "checks",
      description: "Show only check-based loans",
    },
    {
      value: LoanType.STANDING_ORDER,
      labelKey: "loanList.filters.standingOrders",
      icon: "standing_order",
      description: "Show only standing order loans",
    },
  ]);

  /**
   * Get current filter label translation key
   */
  const currentFilterLabel = computed(() => {
    const option = filterOptions.value.find(
      (opt) => opt.value === selectedType.value
    );
    return option?.labelKey || "loanList.filters.all";
  });

  /**
   * Get current filter description
   */
  const currentFilterDescription = computed(() => {
    const option = filterOptions.value.find(
      (opt) => opt.value === selectedType.value
    );
    return option?.description || "";
  });

  /**
   * Check if any filters are active (not default state)
   */
  const hasActiveFilters = computed(() => {
    return selectedType.value !== "all" || searchQuery.value.length > 0;
  });

  /**
   * Count of active filters
   */
  const activeFilterCount = computed(() => {
    let count = 0;
    if (selectedType.value !== "all") count++;
    if (searchQuery.value.length > 0) count++;
    return count;
  });

  /**
   * Check if search is active
   */
  const hasActiveSearch = computed(() => searchQuery.value.length > 0);

  /**
   * Set loan type filter
   * @param type - Loan type to filter by
   */
  const setTypeFilter = (type: LoanType | "all") => {
    selectedType.value = type;
    
    if (import.meta.env.DEV) {
      console.log(`[useLoanFilters] Type filter set to:`, type);
    }
  };

  /**
   * Set search query
   * @param query - Search string
   */
  const setSearchQuery = (query: string) => {
    searchQuery.value = query;
    
    if (import.meta.env.DEV) {
      console.log(`[useLoanFilters] Search query set to:`, query);
    }
  };

  /**
   * Set search query with debounce
   * Useful for real-time search to avoid too many API calls
   * @param query - Search string
   * @param delay - Debounce delay in ms (default: 300)
   */
  const setSearchQueryDebounced = (query: string, delay = 300) => {
    searchQuery.value = query;

    if (searchDebounceTimer) {
      clearTimeout(searchDebounceTimer);
    }

    searchDebounceTimer = setTimeout(() => {
      debouncedSearchQuery.value = query;
      
      if (import.meta.env.DEV) {
        console.log(`[useLoanFilters] Debounced search query:`, query);
      }
    }, delay);
  };

  /**
   * Clear search query
   */
  const clearSearch = () => {
    searchQuery.value = "";
    debouncedSearchQuery.value = "";
    
    if (searchDebounceTimer) {
      clearTimeout(searchDebounceTimer);
      searchDebounceTimer = null;
    }
    
    if (import.meta.env.DEV) {
      console.log("[useLoanFilters] Search cleared");
    }
  };

  /**
   * Clear type filter only
   */
  const clearTypeFilter = () => {
    selectedType.value = "all";
    
    if (import.meta.env.DEV) {
      console.log("[useLoanFilters] Type filter cleared");
    }
  };

  /**
   * Clear all filters and search
   */
  const clearFilters = () => {
    selectedType.value = "all";
    searchQuery.value = "";
    debouncedSearchQuery.value = "";
    
    if (searchDebounceTimer) {
      clearTimeout(searchDebounceTimer);
      searchDebounceTimer = null;
    }
    
    if (import.meta.env.DEV) {
      console.log("[useLoanFilters] All filters cleared");
    }
  };

  /**
   * Toggle filter dropdown open/closed
   */
  const toggleFilterDropdown = () => {
    isFilterDropdownOpen.value = !isFilterDropdownOpen.value;
  };

  /**
   * Open filter dropdown
   */
  const openFilterDropdown = () => {
    isFilterDropdownOpen.value = true;
  };

  /**
   * Close filter dropdown
   */
  const closeFilterDropdown = () => {
    isFilterDropdownOpen.value = false;
  };

  /**
   * Get filter summary for display
   */
  const filterSummary = computed(() => {
    const parts: string[] = [];
    
    if (selectedType.value !== "all") {
      parts.push(selectedType.value);
    }
    
    if (searchQuery.value) {
      parts.push(`"${searchQuery.value}"`);
    }
    
    return parts.length > 0 ? parts.join(" + ") : "No filters";
  });

  /**
   * Export filters as object for API calls
   */
  const getFiltersForAPI = computed(() => ({
    type: selectedType.value === "all" ? undefined : selectedType.value,
    search: debouncedSearchQuery.value || undefined,
  }));

  // Watch selectedType changes (optional - for debugging)
  if (import.meta.env.DEV) {
    watch(selectedType, (newType) => {
      console.log("[useLoanFilters] Selected type changed to:", newType);
    });

    watch(searchQuery, (newQuery) => {
      console.log("[useLoanFilters] Search query changed to:", newQuery);
    });
  }

  return {
    // State
    selectedType,
    searchQuery,
    debouncedSearchQuery,
    isFilterDropdownOpen,

    // Computed
    filterOptions,
    currentFilterLabel,
    currentFilterDescription,
    hasActiveFilters,
    activeFilterCount,
    hasActiveSearch,
    filterSummary,
    getFiltersForAPI,

    // Methods
    setTypeFilter,
    setSearchQuery,
    setSearchQueryDebounced,
    clearSearch,
    clearTypeFilter,
    clearFilters,
    toggleFilterDropdown,
    openFilterDropdown,
    closeFilterDropdown,
  };
}

// Export type for consumers
export type UseLoanFiltersReturn = ReturnType<typeof useLoanFilters>;