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


type UseLoansOptions = {
  includeCompleted?: boolean;
};


export function useLoans(
  options: UseLoansOptions = {}
) {
  const allLoans:
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


  const loans =
    computed(() => {
      const query =
        filters.value.search
          ?.trim()
          .toLowerCase() ||
        "";

      return allLoans.value.filter(
        (loan) => {
          if (
            filters.value.type &&
            filters.value.type !==
              "all" &&
            loan.type !==
              filters.value.type
          ) {
            return false;
          }

          if (
            filters.value.status &&
            filters.value.status !==
              "all" &&
            loan.status !==
              filters.value.status
          ) {
            return false;
          }

          if (!query) {
            return true;
          }

          const searchableValues = [
            loan.borrower.name,
            loan.borrower.phone,
            loan.borrower.email,
            loan.borrower.idNumber,
            loan.trustee?.name,
            loan.trustee?.community,
          ];

          return searchableValues.some(
            (value) =>
              String(
                value || ""
              )
                .toLowerCase()
                .includes(query)
          );
        }
      );
    });


  async function fetchLoans():
    Promise<void> {
    loading.value = true;
    error.value = null;

    try {
      allLoans.value =
        await loanService
          .getLoanDirectory(
            Boolean(
              options.includeCompleted
            )
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

      allLoans.value = [];
    } finally {
      loading.value = false;
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
  }


  function setFilters(
    newFilters:
      Partial<LoanFilters>
  ): void {
    filters.value = {
      ...filters.value,
      ...newFilters,
    };
  }


  function resetFilters():
    void {
    filters.value = {
      type: "all",
      status: "all",
      search: undefined,
    };
  }


  function clearSearch():
    void {
    filters.value = {
      ...filters.value,
      search: undefined,
    };
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
          filters.value.status !==
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


  const statusCounts =
    computed(() => {
      return allLoans.value.reduce(
        (
          counts,
          loan
        ) => {
          counts[
            loan.status
          ] += 1;

          return counts;
        },
        {
          ACTIVE: 0,
          OVERDUE: 0,
          CLOSED: 0,
        }
      );
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
    allLoans,
    loading,
    error,
    filters,
    initialFetchDone,

    hasLoans,
    hasActiveFilters,
    totalAmount,
    loansByType,
    statusCounts,
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