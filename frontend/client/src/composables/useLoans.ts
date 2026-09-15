import {
  computed,
  ref,
} from "vue";

import type {
  ComputedRef,
  Ref,
} from "vue";

import loanService
  from "../services/loanService";

import type {
  LoanFilters,
  LoanListItem,
} from "../types/loan";

import {
  LoanType,
} from "../types/loan";


export function useLoans() {
  const loans:
    Ref<LoanListItem[]> =
      ref([]);

  const loading =
    ref(false);

  const error:
    Ref<string | null> =
      ref(null);

  const filters:
    Ref<LoanFilters> =
      ref({
        type: "all",
        status: "all",
        search: undefined,
      });

  const initialFetchDone =
    ref(false);


  async function fetchLoans():
    Promise<void> {
    loading.value =
      true;

    error.value =
      null;

    try {
      loans.value =
        await loanService
          .getActiveLoans(
            filters.value
          );

      initialFetchDone.value =
        true;
    } catch (
      requestError: any
    ) {
      const status =
        requestError
          ?.response
          ?.status;

      if (
        status === 401
      ) {
        error.value =
          "Authentication required.";
      } else if (
        status === 403
      ) {
        error.value =
          "You do not have permission to view these loans.";
      } else if (
        status === 404
      ) {
        error.value =
          "Loans endpoint was not found.";
      } else if (
        status >= 500
      ) {
        error.value =
          "Server error. Please try again later.";
      } else if (
        requestError
          ?.code ===
          "ECONNABORTED"
      ) {
        error.value =
          "Request timeout. Please check your connection.";
      } else {
        error.value =
          requestError
            ?.response
            ?.data
            ?.detail ||
          "Failed to load loans.";
      }

      loans.value =
        [];
    } finally {
      loading.value =
        false;
    }
  }


  function setFilter<
    K extends keyof LoanFilters
  >(
    key: K,
    value: LoanFilters[K]
  ): void {
    filters.value = {
      ...filters.value,
      [key]: value,
    };

    fetchLoans();
  }


  function setFilters(
    newFilters:
      Partial<LoanFilters>
  ): void {
    filters.value = {
      ...filters.value,
      ...newFilters,
    };

    fetchLoans();
  }


  function resetFilters():
    void {
    filters.value = {
      type: "all",
      status: "all",
      search: undefined,
    };

    fetchLoans();
  }


  function clearSearch():
    void {
    filters.value = {
      ...filters.value,
      search: undefined,
    };

    fetchLoans();
  }


  function retry():
    void {
    fetchLoans();
  }


  function refresh():
    void {
    fetchLoans();
  }


  const hasLoans =
    computed(
      () =>
        loans.value.length >
        0
    );


  const hasActiveFilters:
    ComputedRef<boolean> =
      computed(() => {
        return (
          filters.value.type !==
            "all" ||
          Boolean(
            filters.value
              .search
              ?.trim()
          )
        );
      });


  const totalAmount =
    computed(() => {
      return loans.value.reduce(
        (
          sum,
          loan
        ) =>
          sum +
          Number(
            loan.amount ||
            0
          ),

        0
      );
    });


  const loansByType =
    computed(() => {
      const counts:
        Record<
          LoanType,
          number
        > = {
          [LoanType.CHECKS]:
            0,

          [LoanType.STANDING_ORDER]:
            0,
        };

      for (
        const loan
        of loans.value
      ) {
        counts[
          loan.type
        ] += 1;
      }

      return counts;
    });


  const isLoading =
    computed(
      () =>
        loading.value
    );


  const hasError =
    computed(
      () =>
        error.value !==
        null
    );


  const isEmpty =
    computed(
      () =>
        !loading.value &&
        loans.value.length ===
          0
    );


  return {
    loans,
    loading,
    error,
    filters,
    initialFetchDone,

    hasLoans,
    hasActiveFilters,
    totalAmount,
    loansByType,
    isLoading,
    hasError,
    isEmpty,

    fetchLoans,
    setFilter,
    setFilters,
    resetFilters,
    clearSearch,
    retry,
    refresh,
  };
}


export type UseLoansReturn =
  ReturnType<
    typeof useLoans
  >;