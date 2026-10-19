import api from "./api";

import {
  LoanType,
  type Loan,
  type LoanChecksDetails,
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

    remainingAmount:
      apiLoan.remaining_amount !== undefined
        ? Number(apiLoan.remaining_amount)
        : undefined,

    paidAmount:
      Number(apiLoan.paid_amount || 0),

    paymentsTotal:
      apiLoan.payments_total || 0,

    paymentsPaid:
      apiLoan.payments_paid || 0,

    nextPayment:
      apiLoan.next_payment
        ? {
            dueDate: apiLoan.next_payment.due_date,
            amount: Number(apiLoan.next_payment.amount),
          }
        : null,

    problem:
      apiLoan.problem
        ? {
            count: apiLoan.problem.count,
            missingAmount: Number(apiLoan.problem.missing_amount || 0),
            notes: apiLoan.problem.notes || [],
            firstDueDate: apiLoan.problem.payments?.[0]?.due_date || "",
          }
        : null,

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

    standingOrderFormFileUrl:
      apiLoan.standing_order_form_file_url ||
      null,

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


async function getLoanDirectory(
  includeCompleted = false
): Promise<LoanListItem[]> {
  // One endpoint for every role; it returns balance + problem details too.
  const response =
    await api.get<
      ApiLoanListItem[]
    >(
      "/loans/",
      {
        params: {
          type: "all",
          ...(includeCompleted ? { include_closed: 1 } : {}),
        },
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
  getLoanDirectory,
  getLoanDetails,
};
