import api from "./api";
import type { PaymentScheduleResponse } from "../types/payments";

export async function getLoanPayments(loanId: string): Promise<PaymentScheduleResponse> {
  const res = await api.get(`/loans/${loanId}/payments`);
  return res.data as PaymentScheduleResponse;
}
