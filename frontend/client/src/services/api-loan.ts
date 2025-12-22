import api from "./api"; // axios instance
import { adaptLoanListItem, adaptLoanDetails } from "../adapters/loanAdapter";

export async function fetchLoans(type: string = "all") {
  const response = await api.get("/loans/", {
    params: { type }
  });

  return response.data.map((item: any) => adaptLoanListItem(item));
}

export async function fetchLoanDetails(loanId: string) {
  const response = await api.get(`/loans/${loanId}/`);
  return adaptLoanDetails(response.data);
}

export async function updateLoan(
  loanId: string,
  payload: {
    amount: number;
    start_date: string;
    number_of_payments: number;
    trustee_id: string;
    status: "ACTIVE" | "CLOSED" | "OVERDUE";
  }
) {
  const response = await api.put(`/loans/${loanId}/`, payload);
  return response.data;
}

