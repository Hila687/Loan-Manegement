import api from "./api";

import type {
  ApiLoanDetails,
  ApiLoanListItem,
  ApiLoanUpdatePayload,
} from "../types/api-loan";


export async function fetchLoans(
  type:
    | "all"
    | "checks"
    | "standing_order" =
      "all",
  search = ""
): Promise<ApiLoanListItem[]> {
  const response =
    await api.get<
      ApiLoanListItem[]
    >(
      "/loans/",
      {
        params: {
          type,
          ...(search
            ? {
                search,
              }
            : {}),
        },
      }
    );

  return Array.isArray(
    response.data
  )
    ? response.data
    : [];
}


export async function fetchLoanDetails(
  loanId: string
): Promise<ApiLoanDetails> {
  const response =
    await api.get<ApiLoanDetails>(
      `/loans/${encodeURIComponent(
        loanId
      )}/`
    );

  return response.data;
}


export async function updateLoan(
  loanId: string,
  payload: ApiLoanUpdatePayload
): Promise<ApiLoanDetails> {
  const response =
    await api.put<ApiLoanDetails>(
      `/loans/${encodeURIComponent(
        loanId
      )}/`,
      payload
    );

  return response.data;
}