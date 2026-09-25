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


type ReportLoanRow = {
  loan_id: string;
  loan_type: "checks" | "standing_order";
  borrower_name?: string;
  trustee_name?: string;
  community?: string;
  amount: string | number;
  start_date: string;
  status: "ACTIVE" | "OVERDUE" | "CLOSED";
};


type ManagementReportResponse = {
  loans?: ReportLoanRow[];
};


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


function mapReportLoanListItem(
  row: ReportLoanRow
): LoanListItem {
  return {
    id:
      String(
        row.loan_id
      ),

    type:
      mapLoanType(
        row.loan_type
      ),

    status:
      mapLoanStatus(
        row.status
      ),

    amount:
      Number(
        row.amount ||
          0
      ),

    startDate:
      row.start_date,

    borrower: {
      name:
        String(
          row.borrower_name ||
          ""
        ),

      phone: "",
    },

    trustee:
      row.trustee_name ||
      row.community
        ? {
            name:
              String(
                row.trustee_name ||
                ""
              ),

            community:
              String(
                row.community ||
                ""
              ) ||
              undefined,
          }
        : null,
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
  if (
    includeCompleted
  ) {
    const response =
      await api.get<ManagementReportResponse>(
        "/reports/summary/"
      );

    const rows =
      Array.isArray(
        response.data?.loans
      )
        ? response.data.loans
        : [];

    return rows.map(
      mapReportLoanListItem
    );
  }

  const response =
    await api.get<
      ApiLoanListItem[]
    >(
      "/loans/",
      {
        params: {
          type: "all",
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
