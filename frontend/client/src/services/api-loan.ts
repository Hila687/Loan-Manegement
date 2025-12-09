import api from "./api"; // axios instance
import { adaptLoanListItem, adaptLoanDetails } from "../adapters/loanAdapter";

export async function fetchLoans(type: string = "all") {
  const response = await api.get("/api/loans/", {
    params: { type }
  });

  return response.data.map((item: any) => adaptLoanListItem(item));
}

export async function fetchLoanDetails(loanId: string) {
  const response = await api.get(`/api/loans/${loanId}/`);
  return adaptLoanDetails(response.data);
}
