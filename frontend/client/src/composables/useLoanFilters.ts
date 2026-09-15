import {
  computed,
  ref,
} from "vue";

import type {
  Ref,
} from "vue";

import {
  LoanType,
} from "../types/loan";


export function useLoanFilters() {
  const selectedType:
    Ref<
      LoanType | "all"
    > =
      ref("all");

  const searchQuery =
    ref("");


  const hasActiveFilters =
    computed(() => {
      return (
        selectedType.value !==
          "all" ||
        searchQuery.value
          .trim()
          .length > 0
      );
    });


  function clearSearch():
    void {
    searchQuery.value =
      "";
  }


  function clearTypeFilter():
    void {
    selectedType.value =
      "all";
  }


  function clearFilters():
    void {
    selectedType.value =
      "all";

    searchQuery.value =
      "";
  }


  return {
    selectedType,
    searchQuery,
    hasActiveFilters,

    clearSearch,
    clearTypeFilter,
    clearFilters,
  };
}


export type UseLoanFiltersReturn =
  ReturnType<
    typeof useLoanFilters
  >;