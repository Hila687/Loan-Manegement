// src/services/loanService.ts
import api from "./api";
import type { LoanListItem, LoanFilters } from "../types/loan";
import { LoanType } from "../types/loan";

// This is the raw shape we expect from the backend list endpoint
interface BackendLoanListItem {
  id: string | number;
  borrower: {
    name: string;
    phone: string;
    email?: string | null;
  };
  trustee: {
    name: string;
    community?: string | null;
  };
  amount: number;
  type: LoanType;
  status: string;
  start_date: string;
  num_payments: number;
}

/**
 * Resolve the correct backend endpoint for loans based on filters.
 */
function resolveLoansEndpoint(filters: LoanFilters): string {
  if (filters.type === LoanType.CHECKS) {
    return "/loans/checks/";
  }
  if (filters.type === LoanType.STANDING_ORDER) {
    return "/loans/standing-order/";
  }
  return "/loans/";
}

/**
 * Fetch active loans from backend and map them into LoanListItem objects
 * used by the UI table.
 */
async function getActiveLoans(filters: LoanFilters): Promise<LoanListItem[]> {
  const url = resolveLoansEndpoint(filters);
  const params: Record<string, string> = {};

  if (filters.search) {
    params.search = filters.search;
  }

  const res = await api.get<BackendLoanListItem[]>(url, { params });

  // Map backend shape -> frontend LoanListItem
  const mapped: LoanListItem[] = res.data.map((loan) => ({
    id: String(loan.id),
    borrower_name: loan.borrower?.name ?? "",
    borrower_phone: loan.borrower?.phone ?? "",
    borrower_email: loan.borrower?.email ?? undefined,
    trustee_name: loan.trustee?.name ?? "",
    trustee_community: loan.trustee?.community ?? undefined,
    amount: loan.amount,
    type: loan.type,
    status: loan.status as any,
    start_date: loan.start_date,
    num_payments: loan.num_payments,
  }));

  return mapped;
}

export default {
  getActiveLoans,
};
