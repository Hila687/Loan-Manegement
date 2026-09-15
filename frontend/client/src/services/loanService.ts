import api from "./api";

import {
  LoanType,
  type Loan,
  type LoanChecksDetails,
  type LoanFilters,
  type LoanListItem,
  type LoanStandingOrderDetails,
  type LoanStatus,
} from "../types/loan";

import type {
  ApiLoanDetails,
  ApiLoanListItem,
} from "../types/api-loan";


function mapBorrower(
  apiLoan: ApiLoanListItem
) {
  return {
    name:
      apiLoan.borrower
        ?.name || "",

    phone:
      apiLoan.borrower
        ?.phone || "",

    email:
      apiLoan.borrower
        ?.email || undefined,

    address:
      apiLoan.borrower
        ?.address || undefined,

    idNumber:
      apiLoan.borrower
        ?.id_number ||
      undefined,

    createdAt:
      apiLoan.borrower
        ?.created_at ||
      undefined,
  };
}


function mapTrustee(
  apiLoan: ApiLoanListItem
) {
  if (!apiLoan.trustee) {
    return null;
  }

  return {
    name:
      apiLoan.trustee
        .name || "",

    community:
      apiLoan.trustee
        .community ||
      undefined,

    phone:
      apiLoan.trustee
        .phone ||
      undefined,

    notes:
      apiLoan.trustee
        .notes ??
      null,
  };
}


function mapLoanType(
  value:
    | "checks"
    | "standing_order"
): LoanType {
  return value === "checks"
    ? LoanType.CHECKS
    : LoanType.STANDING_ORDER;
}


function mapLoanStatus(
  value: string
): LoanStatus {
  if (
    value === "OVERDUE"
  ) {
    return "OVERDUE";
  }

  if (
    value === "CLOSED"
  ) {
    return "CLOSED";
  }

  return "ACTIVE";
}


function mapLoanListItem(
  apiLoan: ApiLoanListItem
): LoanListItem {
  return {
    id:
      apiLoan.loan_id,

    type:
      mapLoanType(
        apiLoan.loan_type
      ),

    status:
      mapLoanStatus(
        apiLoan.status
      ),

    amount:
      Number(
        apiLoan.amount ||
          0
      ),

    startDate:
      apiLoan.start_date,

    borrower:
      mapBorrower(
        apiLoan
      ),

    trustee:
      mapTrustee(
        apiLoan
      ),
  };
}


function mapLoanDetails(
  apiLoan: ApiLoanDetails
): Loan {
  let details:
    | LoanChecksDetails
    | LoanStandingOrderDetails;

  if (
    apiLoan.loan_type ===
    "checks"
  ) {
    const apiDetails =
      apiLoan.details;

    details = {
      numPayments:
        Number(
          "num_payments"
            in apiDetails
            ? apiDetails
                .num_payments
            : 0
        ),

      predefinedSchedule:
        "predefined_schedule"
          in apiDetails
          ? Boolean(
              apiDetails
                .predefined_schedule
            )
          : false,

      checkDetails:
        "check_details"
          in apiDetails
          ? apiDetails
              .check_details
          : null,
    };
  } else {
    const apiDetails =
      apiLoan.details;

    details = {
      numPayments:
        Number(
          "num_payments"
            in apiDetails
            ? apiDetails
                .num_payments
            : 0
        ),

      monthlyAmount:
        Number(
          "monthly_amount"
            in apiDetails
            ? apiDetails
                .monthly_amount
            : 0
        ),

      chargeDay:
        Number(
          "charge_day"
            in apiDetails
            ? apiDetails
                .charge_day
            : 0
        ),

      stopDate:
        "stop_date"
          in apiDetails
          ? apiDetails
              .stop_date
          : null,
    };
  }

  return {
    id:
      apiLoan.loan_id,

    type:
      mapLoanType(
        apiLoan.loan_type
      ),

    status:
      mapLoanStatus(
        apiLoan.status
      ),

    amount:
      Number(
        apiLoan.amount ||
          0
      ),

    startDate:
      apiLoan.start_date,

    createdAt:
      apiLoan.created_at,

    formFileUrl:
      apiLoan.form_file_url,

    borrower:
      mapBorrower(
        apiLoan
      ),

    trustee:
      mapTrustee(
        apiLoan
      ),

    details,
  };
}


async function getActiveLoans(
  filters: LoanFilters = {}
): Promise<LoanListItem[]> {
  const params: Record<
    string,
    string
  > = {};

  if (
    filters.type &&
    filters.type !== "all"
  ) {
    params.type =
      String(
        filters.type
      );
  } else {
    params.type =
      "all";
  }

  if (
    filters.status &&
    filters.status !== "all"
  ) {
    params.status =
      String(
        filters.status
      );
  }

  if (
    filters.search
      ?.trim()
  ) {
    params.search =
      filters.search.trim();
  }

  const response =
    await api.get<
      ApiLoanListItem[]
    >(
      "/loans/",
      {
        params,
      }
    );

  const items =
    Array.isArray(
      response.data
    )
      ? response.data
      : [];

  return items.map(
    mapLoanListItem
  );
}


async function getLoanDetails(
  id: string
): Promise<Loan> {
  const response =
    await api.get<
      ApiLoanDetails
    >(
      `/loans/${encodeURIComponent(
        id
      )}/`
    );

  return mapLoanDetails(
    response.data
  );
}


export default {
  getActiveLoans,
  getLoanDetails,
};