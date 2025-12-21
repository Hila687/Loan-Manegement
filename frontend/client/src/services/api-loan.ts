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
