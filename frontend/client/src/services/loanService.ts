// src/services/loanService.ts
import api from "./api";
import {
  LoanType,
  type LoanListItem,
  type Loan,
  type LoanFilters,
  type LoanStatus,
  type LoanDetailsUnion,
} from "../types/loan";
import type { ApiLoanListItem, ApiLoanDetails } from "../types/api-loan";

function mapLoanListItem(apiLoan: ApiLoanListItem): LoanListItem {
  return {
    id: apiLoan.loan_id,
    type:
      apiLoan.loan_type === "checks"
        ? LoanType.CHECKS
        : LoanType.STANDING_ORDER,
    status: apiLoan.status as LoanStatus,
    amount: Number(apiLoan.amount),
    startDate: apiLoan.start_date,

    borrower: {
      name: apiLoan.borrower.name,
      phone: apiLoan.borrower.phone,
      email: apiLoan.borrower.email ?? undefined,
      address: apiLoan.borrower.address,
      idNumber: apiLoan.borrower.id_number,
      createdAt: apiLoan.borrower.created_at,
    },

    trustee: apiLoan.trustee
      ? {
          name: apiLoan.trustee.name,
          community: apiLoan.trustee.community,
          phone: apiLoan.trustee.phone,
          notes: apiLoan.trustee.notes,
        }
      : null,
  };
}

function mapLoanDetails(apiLoan: ApiLoanDetails): Loan {
  let details: LoanDetailsUnion = {};

  if ("num_payments" in apiLoan.details) {
    details = {
      numPayments: apiLoan.details.num_payments,
      predefinedSchedule: apiLoan.details.predefined_schedule,
      checkDetails: apiLoan.details.check_details,
    };
  } else if ("monthly_amount" in apiLoan.details) {
    details = {
      monthlyAmount: Number(apiLoan.details.monthly_amount),
      chargeDay: apiLoan.details.charge_day,
      stopDate: apiLoan.details.stop_date,
    };
  }

  return {
    id: apiLoan.loan_id,
    type:
      apiLoan.loan_type === "checks"
        ? LoanType.CHECKS
        : LoanType.STANDING_ORDER,
    status: apiLoan.status as LoanStatus,
    amount: Number(apiLoan.amount),
    startDate: apiLoan.start_date,
    createdAt: apiLoan.created_at,
    formFileUrl: apiLoan.form_file_url,

    borrower: {
      name: apiLoan.borrower.name,
      phone: apiLoan.borrower.phone,
      email: apiLoan.borrower.email ?? undefined,
      address: apiLoan.borrower.address,
      idNumber: apiLoan.borrower.id_number,
      createdAt: apiLoan.borrower.created_at,
    },

    trustee: apiLoan.trustee
      ? {
          name: apiLoan.trustee.name,
          community: apiLoan.trustee.community,
          phone: apiLoan.trustee.phone,
          notes: apiLoan.trustee.notes,
        }
      : null,

    details,
  };
}

async function getActiveLoans(filters: LoanFilters): Promise<LoanListItem[]> {
  const params: Record<string, string> = {};

  if (filters.status && filters.status !== "all") {
    params.status = String(filters.status);
  } else {
    params.status = "ACTIVE";
  }

  if (filters.type && filters.type !== "all") {
    params.type = filters.type;
  }

  if (filters.search) {
    params.search = filters.search;
  }

  const res = await api.get<ApiLoanListItem[]>("/loans/", { params });
  return res.data.map(mapLoanListItem);
}

async function getLoanDetails(id: string): Promise<Loan> {
  const res = await api.get<ApiLoanDetails>(`/loans/${id}/`);
  return mapLoanDetails(res.data);
}

export default {
  getActiveLoans,
  getLoanDetails,
};
